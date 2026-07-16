from collections.abc import Mapping


def build_headers(*sources: Mapping[str, str] | None, correlation_id: str | None = None, version: str | None = None) -> dict[str, str]:
    result = {"Accept": "application/json", "Content-Type": "application/json"}
    for source in sources:
        if source:
            result.update(source)
    if correlation_id:
        result["X-Correlation-ID"] = correlation_id
    if version:
        result["X-API-Version"] = version
    return result
