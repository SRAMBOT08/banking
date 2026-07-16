from typing import Any
from .serialization import serialize_json


class RequestBuilder:
    def build(self, *, method: str, url: str, params: dict[str, Any] | None = None, json: Any = None) -> dict[str, Any]:
        return {"method": method.upper(), "url": url, "params": params, "json": serialize_json(json)}
