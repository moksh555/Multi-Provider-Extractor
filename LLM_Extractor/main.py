import json
import os
from extractor import Extractor_LLM
from settings import settings
from evaluation import Evaluation
from model_errors import ModelProviderError

def run_evaluation(evaluation, extracted_files_path): 
    labels_files_path = os.path.join(settings.INVOICE_LABELS_BASE_INPUT_PATH)

    for file in os.listdir(extracted_files_path):
        if file in {"evaluation_results.json", "extraction_errors.json"}:
            continue
        extracted_file_path = os.path.join(extracted_files_path, file)
        given_labels_file_path = os.path.join(labels_files_path, file)

        evaluation.evaluate(extracted_file_path, given_labels_file_path)

    report = {
        "correct_result": evaluation.get_correct_result(),
        "incorrect_result": evaluation.get_incorrect_result(),
        "total_result": evaluation.get_total_result(),
        "human_evaluation": evaluation.get_human_evaluation(),
        "accuracy": evaluation.get_accuracy(),
        "correct_result_list": evaluation.get_correct_result_list(),
        "incorrect_result_list": evaluation.get_incorrect_result_list(),
        "human_evaluation_list": evaluation.get_human_evaluation_list(),
    }
    report_path = os.path.join(extracted_files_path, "evaluation_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

def full_run_extraction(extractor, output_path: str, provider: str):
    os.makedirs(output_path, exist_ok=True)
    errors = []

    for file in os.listdir(settings.INVOICE_PDF_BASE_INPUT_PATH):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(settings.INVOICE_PDF_BASE_INPUT_PATH, file)
            try:
                result = extractor.extract_text_from_pdf(pdf_path, provider)
            except ModelProviderError as exc:
                errors.append({
                    "filename": file,
                    "provider": exc.provider,
                    "status_code": exc.status_code,
                    "message": exc.message,
                })
                continue
            out_path = os.path.join(output_path, file.replace(".pdf", ".json"))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2))

    if errors:
        error_path = os.path.join(output_path, "extraction_errors.json")
        with open(error_path, "w", encoding="utf-8") as f:
            json.dump(errors, f, indent=2)

def single_run_extraction(extractor, pdf_path: str, provider: str, output_path: str):
    result = extractor.extract_text_from_pdf(pdf_path, provider)
    file = pdf_path.split("/")[-1]
    os.makedirs(output_path, exist_ok=True)
    out_path = os.path.join(output_path, file.replace(".pdf", ".json"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))

if __name__ == "__main__":
    extractor = Extractor_LLM()
    evaluation = Evaluation()

    # Full extraction
    full_run_extraction(extractor, settings.INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA, "openai")
    run_evaluation(evaluation, settings.INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA)

    # Single extraction
    pdf_path = os.path.join(settings.INVOICE_PDF_BASE_INPUT_PATH, "INV-2026-0001.pdf")
    providers = [
        ("anthropic", settings.INVOICE_PDF_BASE_OUTPUT_PATH_ANTHROPIC_HAIKU),
        ("openai", settings.INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA),
    ]
    for provider, output_path in providers:
        single_run_extraction(extractor, pdf_path, provider, output_path)
