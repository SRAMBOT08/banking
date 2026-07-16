from pydantic import BaseModel, ConfigDict


class BaseIntegrationResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


BaseResponse = BaseIntegrationResponse
