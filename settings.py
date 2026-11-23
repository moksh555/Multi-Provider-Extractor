from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    INVOICE_PDF_BASE_INPUT_PATH: str = "Multi_Document_OCR_Dataset/invoice/pdfs"
    INVOICE_PDF_BASE_OUTPUT_PATH: str = "Output_Multi_Document_OCR_Dataset/invoice/pdfs"
    INVOICE_LABELS_BASE_INPUT_PATH: str = "Multi_Document_OCR_Dataset/invoice/labels"
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    LANGSMITH_API_KEY: str
    LANGSMITH_TRACING: bool
    LANGSMITH_PROJECT: str
    INVOICE_PDF_BASE_OUTPUT_PATH_OPEN_AI_LUNA: str = "Output_Multi_Document_OCR_Dataset/invoice/pdfs/open_ai_luna"
    INVOICE_PDF_BASE_OUTPUT_PATH_ANTHROPIC_HAIKU: str = "Output_Multi_Document_OCR_Dataset/invoice/pdfs/anthropic_haiku"

    model_config = SettingsConfigDict(
        env_file= ".env",
        env_file_encoding= "utf-8",
    )

settings = Settings()