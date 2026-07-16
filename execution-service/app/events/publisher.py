from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from confluent_kafka import Producer

from app.config.settings import Settings
from app.core.logger import get_logger
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.sentineliq_shared.events.autonomous import ExecutionCompletedEvent
from uuid import NAMESPACE_URL, uuid5

logger = get_logger("execution_publisher")


class ExecutionEventPublisher:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._producer = Producer({"bootstrap.servers": settings.kafka_bootstrap}) if settings.kafka_bootstrap else None

    def publish(self, topic: str, key: str, payload: dict[str, Any]) -> None:
        if not self._producer:
            logger.info("event_publish_skipped", extra={"topic": topic, "reason": "producer_disabled"})
            return
        self._producer.produce(topic, key=key.encode(), value=json.dumps(payload, sort_keys=True).encode())
        self._producer.poll(0)
        self._producer.flush(5)

    def publish_plan_created(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.plan_created_topic, key, payload)

    def publish_policy_checked(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.policy_checked_topic, key, payload)

    def publish_awaiting_approval(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.awaiting_approval_topic, key, payload)

    def publish_approved(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.approved_topic, key, payload)

    def publish_ready(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.ready_topic, key, payload)

    def publish_execution_completed(self, plan, source: dict[str, Any]) -> None:
        event = ExecutionCompletedEvent(
            event_id=uuid5(NAMESPACE_URL, f"execution-completed|{plan.plan_id}"),
            tenant_id=plan.tenant_id,
            correlation_id=plan.correlation_id,
            investigation_id=plan.investigation_id,
            source_id=str(source.get("event_id", plan.plan_id)),
            producer_service=self.settings.service_name,
            idempotency_key=f"execution-completed:{plan.plan_id}",
            execution_id=plan.plan_id,
            status=plan.plan_state.value,
            result={"plan_id": plan.plan_id, "tasks": plan.model_dump(mode="json").get("tasks", [])},
        )
        self.publish(self.settings.completed_topic, plan.plan_id, event.model_dump(mode="json"))

    def publish_started(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.started_topic, key, payload)

    def publish_completed(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.completed_topic, key, payload)

    def publish_failed(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.failed_topic, key, payload)

    def publish_cancelled(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.cancelled_topic, key, payload)

    def publish_verified(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.verified_topic, key, payload)

    def publish_audit(self, payload: dict[str, Any], key: str) -> None:
        self.publish(self.settings.audit_topic, key, payload)
