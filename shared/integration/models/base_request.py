from pydantic import BaseModel, ConfigDict


class BaseIntegrationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")


BaseRequest = BaseIntegrationRequest
