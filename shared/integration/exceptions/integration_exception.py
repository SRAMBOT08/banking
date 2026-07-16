class IntegrationException(RuntimeError):
    """Base exception raised by the Platform Integration SDK."""

    def __init__(self, message: str, *, service: str | None = None, endpoint: str | None = None, cause: Exception | None = None):
        super().__init__(message)
        self.service = service
        self.endpoint = endpoint
        self.cause = cause
