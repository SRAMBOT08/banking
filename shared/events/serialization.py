from __future__ import annotations

from typing import Type

from pydantic import BaseModel


def serialize_event(event: BaseModel) -> str:
    return event.model_dump_json()


def deserialize_event(payload: str, model: Type[BaseModel]) -> BaseModel:
    return model.model_validate_json(payload)
