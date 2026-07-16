from pydantic import BaseModel, Field


class IntegrationErrorModel(BaseModel):
    message: str
    code: str = "integration_error"
    service: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    details: dict = Field(default_factory=dict)


ErrorModel = IntegrationErrorModel
