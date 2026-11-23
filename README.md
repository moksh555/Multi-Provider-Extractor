# Multi-Provider Extractor

`LLM_Extractor` reads an invoice PDF, sends it to Claude Haiku or GPT-6 Luna, and saves one structured invoice plus token counts and a price. It can then score that JSON against a gold label file that has the same name.

`ModelGateaway` is the single place that talks to a model. The extractor encodes the PDF once, then the gateway sends that same document and the same `ExtractionRequest` schema to whichever provider you name. Today that is Claude Haiku (`"anthropic"`) or GPT-6 Luna (`"openai"`). Retries, pricing, and the saved JSON shape stay the same, so comparing providers is a name in the call rather than a second pipeline. A later provider is another entry in that gateway, as described in [Adapt this to other PDFs](#adapt-this-to-other-pdfs).

Run it from the project root:

```bash
PYTHONPATH=. uv run LLM_Extractor/main.py
```

`PYTHONPATH=.` puts the project root on the import path so `settings` can be imported. Python 3.13 and [uv](https://docs.astral.sh/uv/) are the expected toolchain. Install dependencies with `uv sync`.

`if __name__ == "__main__"` in `LLM_Extractor/main.py` runs both sections below. Comment out the section you do not want.

The full extraction calls `full_run_extraction` with provider `"openai"` and writes every PDF into `INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA`. It then calls `run_evaluation` on that folder.

The single extraction joins `INVOICE_PDF_BASE_INPUT_PATH` with `INV-2026-0001.pdf` and loops this provider list:

- `"anthropic"` writes to `INVOICE_PDF_BASE_OUTPUT_PATH_ANTHROPIC_HAIKU`
- `"openai"` writes to `INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA`

A provider you add later is one more pair in that list, plus the pieces in [Adapt this to other PDFs](#adapt-this-to-other-pdfs).

## API keys

Set the secrets in a `.env` file in the project root, or export them in the shell. `Settings` reads either source. Do not commit `.env`.

```env
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=document-classifier
```

Where each key comes from:

- `ANTHROPIC_API_KEY`: Claude Console, Settings, API keys. https://console.anthropic.com/settings/keys
- `OPENAI_API_KEY`: OpenAI platform API keys. https://platform.openai.com/api-keys
- `LANGSMITH_API_KEY`: LangSmith settings, API keys. https://smith.langchain.com/
- `LANGSMITH_TRACING`: set to `true` to record traces.
- `LANGSMITH_PROJECT`: the LangSmith project used by the OpenAI `wrap_openai` client. Anthropic does not read this variable. To put both providers in one LangSmith project, set the Claude destination Project field to this same name. To keep them apart, set a different name there.

Either the `.env` file or this export is enough for the app. `wrap_openai` only sees the process environment, so OpenAI tracing still needs `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, and `LANGSMITH_PROJECT` exported even when the other keys live only in `.env`.

```bash
export ANTHROPIC_API_KEY=your-anthropic-key
export OPENAI_API_KEY=your-openai-key
export LANGSMITH_API_KEY=your-langsmith-key
export LANGSMITH_TRACING=true
export LANGSMITH_PROJECT=document-classifier
```

The Anthropic client in this repo is not wrapped. OpenAI traces come from `wrap_openai`. Claude traces come from the Console destination in [LangSmith tracing for Claude](#langsmith-tracing-for-claude).

## Adapt this to other PDFs

Change these in order when the documents, folders, fields, or models are yours.

1. Input PDFs. Set `INVOICE_PDF_BASE_INPUT_PATH` in `settings.py`. The full run lists that folder and keeps names that end in `.pdf`.
2. Gold labels. Set `INVOICE_LABELS_BASE_INPUT_PATH`. Evaluation looks up a label by the output JSON name, so `invoice.pdf` is scored against `invoice.json` in the labels folder.
3. Output folders. Set `INVOICE_PDF_BASE_OUTPUT_PATH`, `INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA`, and `INVOICE_PDF_BASE_OUTPUT_PATH_ANTHROPIC_HAIKU`. Each provider writes into its own folder so the JSON files do not overwrite each other. `evaluation_results.json` and `extraction_errors.json` are written into the output folder you pass to the run.
4. Which file and which providers run. In `LLM_Extractor/main.py`, change the `pdf_path` inside the single-extraction section, and change the `providers` list. Each entry is `(provider name, output folder from settings)`. The full-extraction call takes one provider string and one output path.
5. A new provider, including its price. Add all of these:
   - a `(name, output path)` entry in the `providers` list
   - an output-path field in `settings.py`
   - a branch in `Extractor_LLM._extract_with_provider`
   - an extraction method on `ModelGateaway`
   - an entry in `PRICING` in `LLM_Extractor/model_pricing.py`, with `input`, `output`, `cache_write`, and `cache_read` as USD per 1,000,000 tokens
   - a pricing method on `PricingGateway`
   - that method's name in `ModelGateaway._get_model_pricing_mapper`
6. Different fields. Change the fields on `ExtractionRequest` and, when line items differ, the fields on `Items` in `LLM_Extractor/pydantic_models.py`. Do not rename `ExtractionRequest`, `Items`, `ExtractionsResponse`, or `PricingResponse`. `ModelGateaway` passes the class `ExtractionRequest` as `output_format` and `text_format`, and `ExtractionsResponse` stores the result on the field `ExtractionRequests`. Anthropic structured outputs allow at most 16 nullable fields in this schema, including nested models. Label JSON keys must match the field names the model returns under `ExtractionRequests[0]`.
7. The prompt. Rewrite the text of `PDF_EXTRACTION_PROMPT` in `LLM_Extractor/prompt/pdf_extraction_prompt.py`. Both providers send this same constant, so one edit covers Claude and OpenAI. Keep the constant name `PDF_EXTRACTION_PROMPT`. Do not paste the field list into the prompt. `ExtractionRequest` is already the schema. Change the parts that describe the documents: which fields may be null, the date and number formats, and the checks that set `calculation_status` and `calculation_reason`.

`extract_text_from_pdf(pdf_path, provider)` reads a local file. `base64_encode_pdf` turns that file into the raw standard base64 string the providers receive. It is not a `data:application/pdf;base64,...` URL. The OpenAI request adds that prefix itself.

## LangSmith tracing for Claude

Claude traces in this setup come from the Claude Platform, not from a wrapper in `model_gateaway.py`. The platform sends OpenTelemetry traces of Messages API requests to a destination you register in the Claude Console. The Anthropic call in this repo does not need a code change for that path. The official guide is [Trace with Anthropic](https://docs.langchain.com/langsmith/trace-anthropic).

The installed package `opentelemetry-instrumentation-anthropic` is not wired up in the gateway. This section is the Console destination only.

You need an admin role in the Claude Console organization, or an equivalent permission, and a LangSmith API key.

1. In the Claude Console, open the organization OpenTelemetry settings and click Add destination.
2. Set Provider to LangSmith. The form switches to the LangSmith fields.
3. Set Region to the LangSmith deployment you use. US is `https://api.smith.langchain.com`. The OpenTelemetry base URL is that LangSmith API URL plus `/otel`, for example `https://api.smith.langchain.com/otel`. Do not add `/v1/traces`. The exporter adds that path, and including it sends traces to the wrong URL.
4. Paste the LangSmith API key.
5. Set Project to the LangSmith project name, the same value as `LANGSMITH_PROJECT`. If you are sending traces to a LangSmith agent environment, use that environment's `tracer_session_name` instead. An empty Project sends traces to `default`.
6. Leave LangSmith workspace ID empty unless the key is an organization-scoped service key. An empty workspace sends traces to the workspace that owns the key.
7. Set Content mode. Full content includes prompts and responses, which means the invoice text is stored in the trace. Metadata only leaves the document content out of the spans.
8. Choose which Claude workspaces send to this destination: All, Selected, or All except. Then click Add destination.

After a Messages API call, the traces show in that LangSmith project.

When you edit the destination later, the form shows a generic OTLP endpoint and request headers. Those headers are `x-api-key` for the LangSmith key, `Langsmith-Project` for the project, and `X-Tenant-Id` for the workspace ID when you set one. If you change the endpoint host, enter the header values again.

## Function reference

### `settings.py`

`Settings` is a Pydantic settings model. On import it reads `.env` and builds one `settings` object used by the rest of the app.

- `INVOICE_PDF_BASE_INPUT_PATH` is the folder of source PDFs. The default is `Multi_Document_OCR_Dataset/invoice/pdfs`.
- `INVOICE_PDF_BASE_OUTPUT_PATH` is the parent output folder. The default is `Output_Multi_Document_OCR_Dataset/invoice/pdfs`.
- `INVOICE_LABELS_BASE_INPUT_PATH` is the folder of gold JSON labels. The default is `Multi_Document_OCR_Dataset/invoice/labels`.
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `LANGSMITH_API_KEY` are required strings from `.env`.
- `LANGSMITH_TRACING` is a required bool from `.env`.
- `LANGSMITH_PROJECT` is a required string from `.env`.
- `INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA` is the GPT-6 Luna output folder.
- `INVOICE_PDF_BASE_OUTPUT_PATH_ANTHROPIC_HAIKU` is the Claude Haiku output folder.

`model_config` tells Pydantic to load `.env` with UTF-8. `settings = Settings()` is the shared instance.

### `LLM_Extractor/extractor.py`

`Extractor_LLM.__init__` takes no arguments and stores nothing. A new `ModelGateaway` is created on each extraction.

`base64_encode_pdf(pdf_path)` opens the PDF as bytes, encodes it with standard base64, and returns that text. The caller still needs the original filename separately when the provider is OpenAI.

`extract_text_from_pdf(pdf_path, provider)` encodes the local PDF, takes the filename from the last `/` segment of the path, and returns the `ExtractionsResponse` from `_extract_with_provider`.

`_extract_with_provider(provider, pdf_data, filename)` builds a map from `"anthropic"` to `antropic_haiku_pdf_extraction` and from `"openai"` to `openai_luna_pdf_extraction`, then calls the matching function. An unknown name raises `ValueError`.

### `LLM_Extractor/model_gateaway.py`

`ModelGateaway._RETRYABLE_ERRORS` is the class-level tuple of temporary Anthropic and OpenAI errors: rate limit, timeout, connection failure, and internal server error.

`ModelGateaway.__init__` builds an Anthropic client from `settings.ANTHROPIC_API_KEY`, a `PricingGateway`, and an OpenAI client from `settings.OPENAI_API_KEY` wrapped by `wrap_openai`.

`antropic_haiku_pdf_extraction(base_64_encoded_pdf)` sends the PDF and `PDF_EXTRACTION_PROMPT` to `claude-haiku-5-5` through `messages.parse`, with `ExtractionRequest` as the output format. The call goes through `_call_provider`. The return value is an `ExtractionsResponse` with the parsed invoice, input tokens, output tokens, thinking tokens, the model name, and a price. Cache write and cache read tokens from the Anthropic usage object are included in that price.

`openai_luna_pdf_extraction(base_64_encoded_pdf, filename)` sends the PDF and the same prompt to `gpt-6-luna` through `responses.parse`. The file payload is `data:application/pdf;base64,` plus the raw base64 string, and the filename is sent with it. The return value is an `ExtractionsResponse`. Thinking tokens come from `reasoning_tokens`. Cache counts passed into pricing are `0` and `0`.

`_call_provider(provider, call)` runs `call` up to three times. `call` is the API request, passed in as a function that has not run yet. Temporary errors in `_RETRYABLE_ERRORS` wait 2 seconds after the first failure and 4 seconds after the second. The third temporary failure raises `ModelProviderError` with `retryable=True`. Any other Anthropic `APIError`, OpenAI `APIError`, `LengthFinishReasonError`, or `ContentFilterFinishReasonError` raises immediately with `retryable=False`. The original provider exception stays attached.

`_provider_error(provider, exc, retryable)` copies the provider name, HTTP status when the exception has one, the exception text, and the `retryable` flag onto a `ModelProviderError`. It does not decide whether to retry.

`_get_model_pricing_mapper(model)` returns the pricing method name for `"claude-haiku-5-5"` or `"gpt-6-luna"`. Any other model name raises `KeyError`.

`_get_pricing(model, input_tokens, output_tokens, cache_write_tokens=0, cache_read_tokens=0)` looks up that method on `PricingGateway` and returns its `PricingResponse`.

### `LLM_Extractor/model_errors.py`

`ModelProviderError` is the single error type the batch loop catches. It stores `provider`, `status_code`, `message`, and `retryable`. `full_run_extraction` records `provider`, `status_code`, and `message` in `extraction_errors.json` and continues with the next PDF. `single_run_extraction` does not catch it, so the script stops.

### `LLM_Extractor/main.py`

`full_run_extraction(extractor, output_path, provider)` creates the output folder, then extracts every `.pdf` in `INVOICE_PDF_BASE_INPUT_PATH` with that one provider. Each success is written as `<name>.json` in `output_path`. A `ModelProviderError` is stored and the loop continues. If any file failed, the list is written to `extraction_errors.json` in that same folder.

`single_run_extraction(extractor, pdf_path, provider, output_path)` extracts one local PDF with one provider and writes `<filename>.json` into `output_path`. A provider error propagates.

`run_evaluation(evaluation, extracted_files_path)` scores every JSON file in the output folder except `evaluation_results.json` and `extraction_errors.json`. For each file it loads the matching name from `INVOICE_LABELS_BASE_INPUT_PATH` and calls `evaluation.evaluate`. It then writes the counts, accuracy, and the three result lists to `evaluation_results.json` in the output folder.

### `LLM_Extractor/evaluation.py`

`Evaluation.__init__` starts the correct, incorrect, total, and human-review counters at 0 and starts three empty lists.

`evaluate(extracted_result_path, given_labels_path)` loads both JSON files. It increments `total_result` once per file. For each key in the label, it compares that value with `ExtractionRequests[0][field]`. Two strings match when they are equal after lowercasing and stripping. Every other type uses `==`. The first mismatch appends `[filename, field, label, extracted, "Incorrect"]` to the incorrect list, increments `incorrect_result`, and returns, so the rest of that invoice is not scored. A label key missing from the extraction is treated as incorrect and also returns. When every label field matches, it increments `correct_result` and appends one correct row. If `calculation_status` is `"Human-Evaluation-Required"`, it also increments `human_evaluation` and stores the file, the last field, both values, and `calculation_reason`.

`get_correct_result`, `get_incorrect_result`, `get_total_result`, and `get_human_evaluation` return those counters.

`get_accuracy` returns `correct_result / total_result`.

`get_correct_result_list`, `get_incorrect_result_list`, and `get_human_evaluation_list` return the row lists.

### `LLM_Extractor/model_pricing.py`

`PRICING` maps a model name to USD rates per 1,000,000 tokens: `input`, `output`, `cache_write`, and `cache_read`. The current models are `claude-haiku-5-5` and `gpt-6-luna`.

### `LLM_Extractor/pricing_gateway.py`

`PricingGateway.get_pricing_claude_haiku(input_tokens, output_tokens, cache_write_tokens=0, cache_read_tokens=0)` multiplies the Haiku rates by the token counts, divides by 1,000,000, and returns a `PricingResponse`. Cache prices are `None` when that token count is 0. `Total_price` is the sum of the four amounts.

`PricingGateway.get_pricing_gpt_luna` does the same calculation with the `gpt-6-luna` rates.

### `LLM_Extractor/pydantic_models.py`

`Items` is one invoice line. `description`, `quantity`, `unit_price`, and `amount` are all required.

`ExtractionRequest` is one invoice. Required fields include the invoice identity, company, customer, invoice date, currency, status, `items`, subtotal, total, balance due, and `calculation_status`. These fields may be null when they are not printed: `due_date`, `payment_terms`, `discount`, `tax_rate`, `tax`, `shipping`, `amount_paid`, `vendor_email`, `vendor_phone`, `po_number`, and `calculation_reason`. `calculation_status` is `"Pass"` only when every printed field is present and the arithmetic checks hold. Otherwise it is `"Human-Evaluation-Required"`. `calculation_reason` is null on pass, and on human review it names each missing field and each failed check.

`PricingResponse` holds the dollar amounts for input, output, cache write, cache read, and the total.

`ExtractionsResponse` holds a list of `ExtractionRequest`, the token counts, `Output_thinking_tokens`, the model name, and `Pricing`.

### `LLM_Extractor/prompt/pdf_extraction_prompt.py`

`PDF_EXTRACTION_PROMPT` is the instruction sent as the user text for both providers. It tells the model to fill only the schema supplied with the request, so the prompt does not repeat the field list. It also sets the date format, the number format, which fields may be null, and the arithmetic checks that decide `calculation_status`.

## Dataset

The PDFs and labels in `Multi_Document_OCR_Dataset` come from [Multi-Document Dataset for OCR, Document AI, and LLM](https://www.kaggle.com/datasets/miadul/multi-document-dataset-for-ocr-document-ai-and-llm?resource=download) by Arif Miah.
