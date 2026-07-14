from __future__ import annotations

from typing import Dict, Tuple, Type

from pydantic import BaseModel


class EventRegistryError(Exception):
    pass


class DuplicateEventRegistrationError(EventRegistryError):
    pass


class UnknownEventError(EventRegistryError):
    pass


class EventRegistry:
    """Registry for event types and versions.

    Usage:
    - register_event(name, version, model)
    - lookup(name, version) -> model
    """

    _registry: Dict[Tuple[str, str], Type[BaseModel]] = {}

    @classmethod
    def register_event(cls, name: str, version: str, model: Type[BaseModel]) -> None:
        key = (name, version)
        if key in cls._registry:
            raise DuplicateEventRegistrationError(f"Event {name}@{version} already registered")
        cls._registry[key] = model

    @classmethod
    def get_event(cls, name: str, version: str) -> Type[BaseModel]:
        key = (name, version)
        model = cls._registry.get(key)
        if model is None:
            raise UnknownEventError(f"Event {name}@{version} not found in registry")
        return model

    @classmethod
    def list_events(cls) -> Dict[Tuple[str, str], Type[BaseModel]]:
        return dict(cls._registry)
