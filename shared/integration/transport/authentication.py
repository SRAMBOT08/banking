from typing import Mapping


class Authentication:
    def headers(self) -> Mapping[str, str]:
        return {}


class BearerAuthentication(Authentication):
    def __init__(self, token: str):
        self.token = token

    def headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
