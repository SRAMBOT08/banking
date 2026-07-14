from __future__ import annotations

from typing import Type

from .base import BaseEvent
from ..enums.types import EventType


class AuthenticationEvent(BaseEvent):
    event_type: EventType = EventType.AUTHENTICATION


class TransactionEvent(BaseEvent):
    event_type: EventType = EventType.TRANSACTION


class ThreatEvent(BaseEvent):
    event_type: EventType = EventType.THREAT


class IdentityEvent(BaseEvent):
    event_type: EventType = EventType.IDENTITY


class AssetEvent(BaseEvent):
    event_type: EventType = EventType.ASSET


class FraudEvent(BaseEvent):
    event_type: EventType = EventType.FRAUD


class EvidenceEvent(BaseEvent):
    event_type: EventType = EventType.EVIDENCE


class InvestigationEvent(BaseEvent):
    event_type: EventType = EventType.INVESTIGATION


class DecisionEvent(BaseEvent):
    event_type: EventType = EventType.DECISION


class ExecutionEvent(BaseEvent):
    event_type: EventType = EventType.EXECUTION
