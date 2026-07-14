from __future__ import annotations

from dataclasses import dataclass

from app.config.settings import AdapterSettings
from app.models import AuthenticationContext


@dataclass(frozen=True)
class BasicAuthProvider:
    username: str
    password: str

    @classmethod
    def from_settings(cls, settings: AdapterSettings) -> "BasicAuthProvider":
        return cls(username=settings.servicenow_username, password=settings.servicenow_password)

    def context(self) -> AuthenticationContext:
        return AuthenticationContext(mode="basic", username=self.username)

    def auth_tuple(self) -> tuple[str, str]:
        return self.username, self.password
