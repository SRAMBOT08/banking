import httpx
from ..exceptions import IntegrationTimeoutError, ServiceException


def map_transport_error(exc: BaseException, *, service: str, endpoint: str):
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        return IntegrationTimeoutError(f"{service} request timed out", service=service, endpoint=endpoint, cause=exc)
    if isinstance(exc, httpx.HTTPStatusError):
        return ServiceException(f"{service} returned HTTP {exc.response.status_code}", service=service, endpoint=endpoint, status_code=exc.response.status_code, cause=exc)
    if isinstance(exc, httpx.HTTPError):
        return ServiceException(f"{service} request failed", service=service, endpoint=endpoint, cause=exc)
    return exc
