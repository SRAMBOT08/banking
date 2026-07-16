from __future__ import annotations
from typing import Any

# Placeholder for LangGraph imports; the actual graph construction lives in planner.py
# This module centralizes helpers for node wiring and common utilities.

def attach_logging(node_func: Any) -> Any:
    """Decorator helper to attach structured logging to node call sites if needed."""

    def wrapper(*args, **kwargs):
        return node_func(*args, **kwargs)

    return wrapper
