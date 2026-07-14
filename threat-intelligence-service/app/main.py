from fastapi import FastAPI
from app.core.logger import get_logger
from app.config.settings import settings
from app.knowledge_registry.manager import RegistryManager
from app.infrastructure.kafka_client import KafkaConsumerWrapper, KafkaProducerWrapper
from app.engine.matcher import match_pattern_graph
from app.engine.confidence import propagate_confidence
from app.engine.explainability import explain_match
from app.models.candidate import InvestigationCandidate
from app.repositories.candidates_repo import InMemoryCandidatesRepo
import json

logger = get_logger("threat-intel")
app = FastAPI(title=settings.service_name)

# init components
registry = RegistryManager(settings.patterns_dir)
registry.load()
producer = KafkaProducerWrapper()
consumer = KafkaConsumerWrapper(settings.consumer_topic)
candidates_repo = InMemoryCandidatesRepo()


async def handle(msg):
    try:
        raw = msg.value()
        s = raw.decode() if isinstance(raw, (bytes, bytearray)) else str(raw)
        doc = json.loads(s)
        tenant = doc.get('tenant_id', 'tenant-unknown')
        correlation = doc.get('correlation_id')
        investigation_id = doc.get('investigation_id')
        evidence_graph = doc.get('evidence_graph') or doc

        for pattern in registry.list_attack_patterns():
            if pattern.version != registry.get_latest_pattern(pattern.name).version:
                continue
            pname = pattern.name
            matched, missing, matched_edges = match_pattern_graph(registry, pname, evidence_graph)
            score, breakdown = propagate_confidence(pattern, matched, missing)
            explanation = explain_match(pname, matched, missing, breakdown, score, matched_edges)
            if score >= settings.score_threshold:
                mitre_map = registry.get_mitre((pattern.mitre or {}).get('technique', '')) if pattern.mitre else None
                cand = InvestigationCandidate.create(tenant_id=tenant, correlation_id=correlation, pattern_name=pname, pattern_version=str(pattern.version), confidence=score, explanation={**explanation, 'mitre': mitre_map}, evidence_refs=[], investigation_id=investigation_id)
                candidates_repo.save(cand.model_dump())
                producer.produce(settings.producer_topic, key=cand.candidate_id.encode(), value=cand.model_dump_json().encode())
                producer.flush()
                logger.info("candidate_emitted", extra={"candidate_id": cand.candidate_id, "pattern": pname, "confidence": score, "tenant_id": tenant})
    except Exception as exc:
        logger.error("processing_failed", extra={"error": str(exc)})


@app.on_event('startup')
async def startup():
    logger.info('startup', extra={'service': settings.service_name})
    consumer.start(handle)


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': settings.service_name}


@app.get('/api/v1/debug/candidates')
async def debug_candidates():
    return {'candidates': candidates_repo.list_all()}
