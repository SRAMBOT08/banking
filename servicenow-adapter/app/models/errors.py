from enum import Enum
from typing import Any, Dict


class AdapterErrorCode(str, Enum):
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    AUTHORIZATION_FAILURE = "AUTHORIZATION_FAILURE"
    TIMEOUT = "TIMEOUT"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    RATE_LIMITING = "RATE_LIMITING"
    DUPLICATE_REQUEST = "DUPLICATE_REQUEST"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    UNEXPECTED_RESPONSE = "UNEXPECTED_RESPONSE"
    SERVER_ERROR = "SERVER_ERROR"
    RETRY_EXHAUSTION = "RETRY_EXHAUSTION"


class AdapterError(Exception):
    def __init__(self, code: AdapterErrorCode, message: str, details: Dict[str, Any] | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code.value}: {message}")
