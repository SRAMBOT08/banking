from __future__ import annotations

from app.core.logger import get_logger
from app.pipeline.validator import validate_raw_message, ValidationError
from app.pipeline.normalizer import normalize
from app.pipeline.enricher import enrich
from app.pipeline.deduper import Deduper, DuplicateEvent
from app.pipeline.publisher import Publisher

logger = get_logger("orchestrator")


class PipelineOrchestrator:
    def __init__(self, deduper: Deduper, publisher: Publisher):
        self.deduper = deduper
        self.publisher = publisher

    async def handle_message(self, raw_message: bytes):
        # Validation
        try:
            payload_dict, event_model = validate_raw_message(raw_message)
        except ValidationError as exc:
            logger.error("pipeline_validation_failed", extra={"error": str(exc)})
            raise

        # Normalization
        event = normalize(payload_dict, raw_message)

        # Deduplication
        is_dup = await self.deduper.is_duplicate(str(event.event_id), event.model_dump(), {})
        if is_dup:
            logger.info("pipeline_duplicate", extra={"event_id": str(event.event_id)})
            raise DuplicateEvent("duplicate")

        # Enrichment
        event = enrich(event)

        # Publish
        self.publisher.publish_normalized(event)

        return event
