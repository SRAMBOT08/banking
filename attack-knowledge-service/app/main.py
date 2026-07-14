from fastapi import FastAPI
from app.core.logger import get_logger
from app.config.settings import settings
from app.infrastructure.kafka_client import KafkaConsumerWrapper, KafkaProducerWrapper
from app.patterns.loader import load_patterns
from app.engine.matcher import match_pattern
from app.engine.scorer import score_match
from app.engine.explain import explain_candidate
from app.models.models import InvestigationCandidate
from app.repositories.inmemory import InMemoryGraphRepo
import json

logger = get_logger("attack-knowledge")
app = FastAPI(title=settings.service_name)

repo = InMemoryGraphRepo()
patterns = load_patterns(settings.patterns_dir)
producer = KafkaProducerWrapper()


async def handle_message(msg):
    try:
        raw = msg.value()
        s = raw.decode() if isinstance(raw, (bytes, bytearray)) else str(raw)
        doc = json.loads(s)
        # extract metadata
        tenant = doc.get('tenant_id', 'tenant-unknown')
        correlation = doc.get('correlation_id')
        investigation_id = doc.get('investigation_id')
        evidence_graph = doc.get('evidence_graph') or doc

        # iterate patterns
        for pname, pattern in patterns.items():
            matched, missing = match_pattern(pattern, evidence_graph)
            score, breakdown = score_match(pattern, matched, missing)
            explanation = explain_candidate(pname, pattern, matched, missing, breakdown, score, [])
            if score >= settings.score_threshold:
                cand = InvestigationCandidate.make(tenant_id=tenant, correlation_id=correlation or '', pattern=pname, confidence=score, explanation=explanation, evidence_refs=[], investigation_id=investigation_id)
                # persist in-memory and publish
                repo.save_pattern_match(cand.model_dump())
                payload = cand.model_dump_json().encode()
                producer.produce(settings.producer_topic, key=cand.candidate_id.encode(), value=payload)
                producer.flush()
                logger.info("candidate_published", extra={"candidate_id": cand.candidate_id, "pattern": pname, "confidence": score, "tenant_id": tenant})
    except Exception as exc:
        logger.error("processing_failed", extra={"error": str(exc)})


@app.on_event("startup")
async def startup():
    logger.info("startup", extra={"service": settings.service_name})
    consumer = KafkaConsumerWrapper(settings.consumer_topic)
    consumer.start(handle_message)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.get("/api/v1/debug/candidates")
async def list_candidates():
    return {"candidates": repo.list_candidates()}
