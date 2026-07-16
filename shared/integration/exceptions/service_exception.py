from .integration_exception import IntegrationException


class ServiceException(IntegrationException):
    def __init__(self, message: str, *, status_code: int | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
