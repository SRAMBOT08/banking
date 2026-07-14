from __future__ import annotations
import json
from datetime import datetime, timezone
from app.core.logger import get_logger
from app.schemas.candidate import CandidateInput
from app.services.investigation_manager import InvestigationManager
from app.events.kafka import KafkaProducer
from app.config.settings import settings

logger = get_logger("candidate_pipeline")


class CandidatePipeline:
    def __init__(self, manager: InvestigationManager, publisher: KafkaProducer):
        self.manager = manager
        self.publisher = publisher

    async def handle(self, message):
        try:
            raw = message.value()
            payload = json.loads(raw.decode() if isinstance(raw, (bytes, bytearray)) else raw)
            candidate = CandidateInput.model_validate(payload)
            investigation = self.manager.process(candidate)
            timestamp = datetime.now(timezone.utc).isoformat()
            self.publisher.publish_investigation(settings.producer_topic, "INVESTIGATION_ACTIVE", investigation, timestamp)
            self.publisher.publish_investigation(settings.updated_topic, "INVESTIGATION_UPDATED", investigation, timestamp)
            if investigation.state.value == "CLOSED":
                self.publisher.publish_investigation(settings.closed_topic, "INVESTIGATION_CLOSED", investigation, timestamp)
            if investigation.state.value == "ESCALATED":
                self.publisher.publish_investigation(settings.escalated_topic, "INVESTIGATION_ESCALATED", investigation, timestamp)
        except Exception as exc:
            logger.error("candidate_processing_failed", extra={"error": str(exc)})
