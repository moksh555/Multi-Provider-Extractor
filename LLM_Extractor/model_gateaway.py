import time
import anthropic
from settings import settings
from pydantic_models import ExtractionRequest, ExtractionsResponse
from pricing_gateway import PricingGateway
from prompt.pdf_extraction_prompt import PDF_EXTRACTION_PROMPT
from model_errors import ModelProviderError
from langsmith.wrappers import wrap_openai
import openai
from openai import OpenAI, LengthFinishReasonError, ContentFilterFinishReasonError

class ModelGateaway:
    _RETRYABLE_ERRORS = (
        anthropic.RateLimitError,
        anthropic.APITimeoutError,
        anthropic.APIConnectionError,
        anthropic.InternalServerError,
        openai.RateLimitError,
        openai.APITimeoutError,
        openai.APIConnectionError,
        openai.InternalServerError,
    )

    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.pricing_gateway = PricingGateway()
        self.openai_client = wrap_openai(OpenAI(api_key=settings.OPENAI_API_KEY))
    
    def antropic_haiku_pdf_extraction(self, base_64_encoded_pdf: str):
        response = self._call_provider("anthropic", lambda: self.anthropic_client.messages.parse(
            model="claude-haiku-5-5",
            max_tokens=10000,
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base_64_encoded_pdf
                            }
                        },
                        {
                            "type": "text",
                            "text": PDF_EXTRACTION_PROMPT
                        }
                ]
                }
            ],
            output_format=ExtractionRequest

        ))

        return ExtractionsResponse(
            ExtractionRequests=[response.parsed_output],
            Input_tokens=response.usage.input_tokens,
            Output_tokens=response.usage.output_tokens,
            Output_thinking_tokens=(
                response.usage.output_tokens_details.thinking_tokens
                if response.usage.output_tokens_details
                else 0
            ),
            model="claude-haiku-5-5",
            Pricing=self._get_pricing("claude-haiku-5-5", response.usage.input_tokens, response.usage.output_tokens, response.usage.cache_creation_input_tokens, response.usage.cache_read_input_tokens)
        )
    
    def openai_luna_pdf_extraction(self, base_64_encoded_pdf: str, filename: str):
        response = self._call_provider("openai", lambda: self.openai_client.responses.parse(
            model="gpt-6-luna",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": filename,
                            "file_data": f"data:application/pdf;base64,{base_64_encoded_pdf}",
                        },
                        {"type": "input_text", "text": PDF_EXTRACTION_PROMPT},
                    ]
                }
            ],
            text_format=ExtractionRequest
        ))
        return ExtractionsResponse(
            ExtractionRequests=[response.output_parsed],
            Input_tokens=response.usage.input_tokens,
            Output_tokens=response.usage.output_tokens,
            Output_thinking_tokens=(
                response.usage.output_tokens_details.reasoning_tokens
                if response.usage.output_tokens_details
                else 0
            ),
            model="gpt-6-luna",
            Pricing=self._get_pricing("gpt-6-luna", response.usage.input_tokens, response.usage.output_tokens, 0, 0)
        )
    
    def _call_provider(self, provider: str, call):
        for attempt in range(3):
            try:
                return call()
            except self._RETRYABLE_ERRORS as exc:
                if attempt == 2:
                    raise self._provider_error(provider, exc, retryable=True) from exc
                time.sleep(2 if attempt == 0 else 4)
            except (
                anthropic.APIError,
                openai.APIError,
                LengthFinishReasonError,
                ContentFilterFinishReasonError,
            ) as exc:
                raise self._provider_error(provider, exc, retryable=False) from exc

    def _provider_error(self, provider: str, exc: Exception, retryable: bool) -> ModelProviderError:
        return ModelProviderError(
            provider=provider,
            status_code=getattr(exc, "status_code", None),
            message=str(exc),
            retryable=retryable,
        )

    def _get_model_pricing_mapper(self, model: str):
        return {
            "claude-haiku-5-5": "get_pricing_claude_haiku",
            "gpt-6-luna": "get_pricing_gpt_luna"
        }[model]

    def _get_pricing(self, model: str, input_tokens: int, output_tokens: int, cache_write_tokens: int = 0, cache_read_tokens: int = 0):
        method = self._get_model_pricing_mapper(model)
        pricing_method = getattr(self.pricing_gateway, method)
        return pricing_method(input_tokens, output_tokens, cache_write_tokens, cache_read_tokens)