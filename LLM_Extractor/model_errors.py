class ModelProviderError(Exception):
    def __init__(self, provider: str, status_code: int | None, message: str, retryable: bool):
        self.provider = provider
        self.status_code = status_code
        self.message = message
        self.retryable = retryable
        super().__init__(message)
