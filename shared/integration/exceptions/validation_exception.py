from .integration_exception import IntegrationException


class IntegrationValidationError(IntegrationException, ValueError):
    pass


ValidationException = IntegrationValidationError
