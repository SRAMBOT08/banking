Unified Event Platform — events package

This package implements the canonical BaseEvent, event categories, registry, errors and helpers.

Design Principles
- All events inherit from `BaseEvent` (Pydantic v2) and are strongly typed.
- Event types are registered in `EventRegistry` and must be versioned.
- Serialization and validation helpers are provided on `BaseEvent`.

Usage
- Define event models by inheriting from `BaseEvent` and register with `EventRegistry`.
