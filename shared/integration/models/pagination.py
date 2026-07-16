from pydantic import BaseModel, Field


class Pagination(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    total: int | None = Field(default=None, ge=0)
