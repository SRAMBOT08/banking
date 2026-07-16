from collections.abc import Mapping
import httpx
from ..exceptions import ServiceException


class ResponseParser:
    def parse(self, response: httpx.Response, *, service: str, endpoint: str) -> Mapping:
        try:
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ServiceException(f"{service} returned an invalid response", service=service, endpoint=endpoint, status_code=response.status_code, cause=exc) from exc
        if not isinstance(payload, Mapping):
            raise ServiceException(f"{service} returned a non-object response", service=service, endpoint=endpoint, status_code=response.status_code)
        return payload
