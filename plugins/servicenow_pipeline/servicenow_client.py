"""Reusable ServiceNow client architecture.

This module provides the transport boundary for all future ServiceNow
communication. It intentionally contains no incident-specific logic, no REST
endpoint knowledge, and no assumptions about higher-level workflow types.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import os
import logging
from typing import Any, Callable, Mapping, Optional
from urllib.parse import urlparse

import requests

from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now, sanitize_response

logger = logging.getLogger(__name__)


class ServiceNowError(RuntimeError):
    """Base exception for ServiceNow client failures."""


class AuthenticationError(ServiceNowError):
    """Raised when authentication configuration is missing or invalid."""


class RequestError(ServiceNowError):
    """Raised when a request cannot be prepared or the response is invalid."""


class ConnectionError(ServiceNowError):
    """Raised when the underlying HTTP transport fails."""


@dataclass(frozen=True, slots=True)
class ServiceNowRetryPolicy:
    """Retry policy for ServiceNow transport operations.

    The client does not implement retry logic itself; this configuration
    exists so future layers can apply consistent retry behavior without changing
    the client API.
    """

    attempts: int = 1
    backoff_seconds: float = 0.0
    retryable_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)


@dataclass(frozen=True, slots=True)
class ServiceNowClientConfig:
    """Configuration for the reusable ServiceNow client.

    The configuration is intentionally generic: it models instance access and
    transport behavior only, not domain objects or REST paths.
    """

    instance_url: str
    authentication_type: str = "basic"
    username: str | None = None
    password: str | None = None
    access_token: str | None = None
    timeout: float = 30.0
    verify_ssl: bool = True
    retry_policy: ServiceNowRetryPolicy = field(default_factory=ServiceNowRetryPolicy)

    def normalized(self) -> "ServiceNowClientConfig":
        """Return a normalized copy of this config.

        This preserves immutability while ensuring the instance URL is cleaned
        up for client use.
        """
        cleaned_url = str(self.instance_url or "").strip().rstrip("/")
        if not cleaned_url:
            raise AuthenticationError("instance_url is required for ServiceNowClientConfig.")
        return replace(self, instance_url=cleaned_url)


class ServiceNowClient:
    """Reusable ServiceNow transport client.

    The client owns HTTP session lifecycle, default headers, configuration
    validation, response normalization, and error conversion. It does not know
    about incident workflows or higher-level business semantics.
    """

    def __init__(
        self,
        config: ServiceNowClientConfig | Mapping[str, Any],
        *,
        logger_: logging.Logger | None = None,
        session_factory: Callable[[], requests.Session] | None = None,
    ) -> None:
        self._logger = logger_ or logger
        self.config = self._coerce_config(config).normalized()
        self._session_factory = session_factory or self._default_session_factory
        self._session: requests.Session | None = None
        self._closed = False

    @staticmethod
    def _coerce_config(config: ServiceNowClientConfig | Mapping[str, Any]) -> ServiceNowClientConfig:
        if isinstance(config, ServiceNowClientConfig):
            return config
        retry_policy = config.get("retry_policy") if isinstance(config, Mapping) else None
        if isinstance(retry_policy, ServiceNowRetryPolicy):
            policy = retry_policy
        elif isinstance(retry_policy, Mapping):
            policy = ServiceNowRetryPolicy(
                attempts=int(retry_policy.get("attempts", 1) or 1),
                backoff_seconds=float(retry_policy.get("backoff_seconds", 0.0) or 0.0),
                retryable_status_codes=tuple(
                    int(code) for code in retry_policy.get("retryable_status_codes", (429, 500, 502, 503, 504))
                ),
            )
        else:
            policy = ServiceNowRetryPolicy()

        env_instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "")
        env_username = os.getenv("SERVICENOW_USERNAME", "")
        env_password = os.getenv("SERVICENOW_PASSWORD", "")
        env_access_token = os.getenv("SERVICENOW_ACCESS_TOKEN", "")
        env_auth_type = os.getenv("SERVICENOW_AUTHENTICATION_TYPE", "")
        env_timeout = os.getenv("SERVICENOW_TIMEOUT", "")
        env_verify_ssl = os.getenv("SERVICENOW_VERIFY_SSL", "")

        def _truthy(text: str, default: bool = True) -> bool:
            lowered = str(text or "").strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
            return default

        def _coerce_timeout(value: Any, fallback: Any) -> float:
            candidate = value if value not in {None, ""} else fallback
            try:
                return float(candidate if candidate not in {None, ""} else 30.0)
            except (TypeError, ValueError):
                return 30.0

        def _coerce_bool(value: Any, fallback: bool) -> bool:
            if value is None or value == "":
                return fallback
            if isinstance(value, bool):
                return value
            lowered = str(value).strip().lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
            return fallback

        return ServiceNowClientConfig(
            instance_url=str(config.get("instance_url") or env_instance_url or "").strip(),
            authentication_type=str(
                config.get("authentication_type") or env_auth_type or ("basic" if (env_username or env_password) else "none")
            ).strip().lower(),
            username=config.get("username") or env_username or None,
            password=config.get("password") or env_password or None,
            access_token=config.get("access_token") or env_access_token or None,
            timeout=_coerce_timeout(config.get("timeout"), env_timeout),
            verify_ssl=_coerce_bool(config.get("verify_ssl"), _truthy(env_verify_ssl, default=True)),
            retry_policy=policy,
        )

    def _default_session_factory(self) -> requests.Session:
        return requests.Session()

    def authenticate(self) -> None:
        """Validate authentication configuration and initialize the session.

        The client does not contact ServiceNow here. It only validates that the
        local authentication settings are complete enough for future requests.
        """
        auth_type = self.config.authentication_type
        if auth_type not in {"basic", "bearer", "oauth", "token", "none"}:
            raise AuthenticationError(f"Unsupported authentication_type: {auth_type!r}")

        if auth_type == "basic":
            if not self.config.username or not self.config.password:
                raise AuthenticationError("Basic authentication requires username and password.")
        elif auth_type in {"bearer", "oauth", "token"}:
            if not self.config.access_token:
                raise AuthenticationError(f"{auth_type.title()} authentication requires access_token.")

        session = self._ensure_session()
        if auth_type == "basic":
            session.auth = (self.config.username or "", self.config.password or "")
        elif auth_type in {"bearer", "oauth", "token"} and self.config.access_token:
            session.headers.update({"Authorization": f"Bearer {self.config.access_token}"})

    def build_headers(self, extra_headers: Optional[Mapping[str, str]] = None) -> dict[str, str]:
        """Build default request headers for future ServiceNow calls."""
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "hermes-servicenow-client/0.1",
        }

        auth_type = self.config.authentication_type
        if auth_type in {"bearer", "oauth", "token"} and self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"

        if extra_headers:
            headers.update({str(key): str(value) for key, value in extra_headers.items()})

        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Prepare and execute a generic ServiceNow request.

        The method is intentionally transport-only: callers supply a method and
        relative path, and the client handles URL normalization, headers,
        response validation, and error normalization.
        """
        corr_id = correlation_id or new_correlation_id()
        start = now()
        session = self._ensure_session()
        normalized_method = str(method or "").strip().upper()
        if not normalized_method:
            raise RequestError("HTTP method is required.")

        normalized_path = str(path or "").strip()
        if not normalized_path:
            raise RequestError("Request path is required.")

        if not normalized_path.startswith("/"):
            normalized_path = f"/{normalized_path}"

        request_headers = self.build_headers(headers)
        request_timeout = timeout if timeout is not None else self.config.timeout

        url = f"{self.config.instance_url}{normalized_path}"
        auth = None
        if self.config.authentication_type == "basic":
            auth = (self.config.username or "", self.config.password or "")
        request_kwargs: dict[str, Any] = {
            "method": normalized_method,
            "url": url,
            "params": params,
            "json": json,
            "data": data,
            "headers": request_headers,
            "timeout": request_timeout,
            "verify": self.config.verify_ssl,
        }
        if auth is not None:
            request_kwargs["auth"] = auth

        self._log_request(
            normalized_method,
            url,
            correlation_id=corr_id,
            params=params,
            body_present=json is not None or data is not None,
        )

        try:
            response = session.request(**request_kwargs)
        except requests.Timeout as exc:
            log_stage(
                self._logger,
                stage="servicenow_request",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"method": normalized_method, "endpoint": normalized_path},
            )
            raise ConnectionError(f"ServiceNow request timed out: {exc}") from exc
        except requests.RequestException as exc:
            log_stage(
                self._logger,
                stage="servicenow_request",
                correlation_id=corr_id,
                success=False,
                duration_ms=elapsed_ms(start),
                error=exc,
                extra={"method": normalized_method, "endpoint": normalized_path},
            )
            raise ConnectionError(f"ServiceNow transport error: {exc}") from exc

        normalized = self._normalize_response(response)
        log_stage(
            self._logger,
            stage="http_response",
            correlation_id=corr_id,
            success=True,
            duration_ms=elapsed_ms(start),
            extra={
                "method": normalized_method,
                "endpoint": normalized_path,
                "status_code": response.status_code,
                "response": sanitize_response(normalized),
            },
        )
        return normalized

    def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._closed:
            return
        session = self._session
        self._session = None
        self._closed = True
        if session is not None:
            session.close()

    def health_check(self) -> dict[str, Any]:
        """Return local readiness information without calling ServiceNow."""
        self._validate_instance_url()
        return {
            "ok": True,
            "instance_url": self.config.instance_url,
            "authentication_type": self.config.authentication_type,
            "verify_ssl": self.config.verify_ssl,
            "timeout": self.config.timeout,
            "retry_policy": {
                "attempts": self.config.retry_policy.attempts,
                "backoff_seconds": self.config.retry_policy.backoff_seconds,
                "retryable_status_codes": list(self.config.retry_policy.retryable_status_codes),
            },
            "session_open": self._session is not None and not self._closed,
        }

    def _ensure_session(self) -> requests.Session:
        self._validate_instance_url()
        if self._closed:
            raise ConnectionError("ServiceNow client has been closed.")
        if self._session is None:
            self._session = self._session_factory()
        if self.config.authentication_type in {"bearer", "oauth", "token"} and self.config.access_token:
            self._session.headers.update({"Authorization": f"Bearer {self.config.access_token}"})
        return self._session

    def _validate_instance_url(self) -> None:
        parsed = urlparse(self.config.instance_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RequestError(f"Invalid ServiceNow instance_url: {self.config.instance_url!r}")

    def _normalize_response(self, response: requests.Response) -> dict[str, Any]:
        if response.status_code >= 400:
            raise RequestError(
                f"ServiceNow request failed with status {response.status_code}: {response.text[:512]}"
            )
        if response.status_code == 204:
            return {}
        try:
            payload = response.json()
        except ValueError as exc:
            raise RequestError("ServiceNow response was not valid JSON.") from exc
        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    def _log_request(
        self,
        method: str,
        url: str,
        *,
        correlation_id: str,
        params: Optional[Mapping[str, Any]] = None,
        body_present: bool = False,
    ) -> None:
        log_stage(
            self._logger,
            stage="servicenow_request",
            correlation_id=correlation_id,
            success=True,
            duration_ms=0.0,
            message="HTTP request prepared",
            extra={
                "method": method,
                "endpoint": urlparse(url).path,
                "params": dict(params or {}),
                "body_present": body_present,
                "timeout": self.config.timeout,
                "verify_ssl": self.config.verify_ssl,
            },
        )
