import base64
from settings import settings
from model_gateaway import ModelGateaway

class Extractor_LLM:
    def __init__(self):
        pass

    def base64_encode_pdf(self, pdf_path: str):
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = base64.standard_b64encode(pdf_file.read()).decode("utf-8")
        return pdf_data
    
    def extract_text_from_pdf(self, pdf_path: str, provider: str):
        pdf_data = self.base64_encode_pdf(pdf_path)
        filename = pdf_path.split("/")[-1]
        return self._extract_with_provider(provider, pdf_data, filename)

    def _extract_with_provider(self, provider: str, pdf_data: str, filename: str):
        model_gateaway = ModelGateaway()
        providers = {
            "anthropic": lambda: model_gateaway.antropic_haiku_pdf_extraction(pdf_data),
            "openai": lambda: model_gateaway.openai_luna_pdf_extraction(pdf_data, filename),
        }
        try:
            return providers[provider]()
        except KeyError:
            raise ValueError(f"Unknown provider: {provider}")
    
