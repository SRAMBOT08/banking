from .integration_exception import IntegrationException


class IntegrationTimeoutError(IntegrationException, TimeoutError):
    pass


TimeoutException = IntegrationTimeoutError
