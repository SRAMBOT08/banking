from fastapi import FastAPI
from app.core.logger import get_logger
from app.config.settings import settings
from app.repo.inmemory import InMemoryGraphRepo
from app.pipeline.graph_engine import GraphEngine
from app.infrastructure.kafka_client import KafkaConsumerWrapper
from app.infrastructure.kafka_client import KafkaEventPublisher
from shared.sentineliq_shared.events.base import BaseEvent
from shared.sentineliq_shared.events.autonomous import EvidenceGraphEvent
from uuid import UUID, uuid5, NAMESPACE_URL
from app.pipeline.extractor import extract
from app.pipeline.resolver import resolve_entities
from app.pipeline.relationship_builder import build_relationships
from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryEvidenceRepository
from app.query.service import EvidenceQueryService

logger = get_logger("main")
app = FastAPI(title="evidence-service")

# in-memory repo used for dev and tests; can be swapped for Neo4j-backed repo later
repo = InMemoryGraphRepo()
engine = GraphEngine(repo)
query_service = EvidenceQueryService(InMemoryEvidenceRepository(repo))
_consumer = None
_publisher = KafkaEventPublisher()
_published_events: set[str] = set()

app.include_router(create_query_router(query_service))


@app.on_event("startup")
async def startup_event():
    global _consumer
    logger.info("startup", extra={"service": settings.service_name})

    # start consumer for normalized topic
    _consumer = KafkaConsumerWrapper(settings.normalized_topic, settings.consumer_group,
                                     dlq_topic=settings.dlq_topic)

    async def handler(msg):
        try:
            raw = msg.value()
            s = raw.decode() if isinstance(raw, (bytes, bytearray)) else str(raw)
            be = BaseEvent.model_validate_json(s)
            logger.info("consumed_normalized", extra={"event_id": str(be.event_id)})

            extracted = extract(be)
            resolved = resolve_entities(extracted)
            rels = build_relationships(resolved)
            engine.apply(resolved, rels)
            investigation_id = str(be.investigation_id) if be.investigation_id else None
            correlation_id = str(be.correlation_id) if be.correlation_id else None
            identity = investigation_id or correlation_id or str(be.event_id)
            event_id = uuid5(NAMESPACE_URL, f"evidence-graph|{identity}|{be.event_id}")
            if str(event_id) not in _published_events:
                graph_event = EvidenceGraphEvent(
                    event_id=event_id,
                    tenant_id=be.tenant_id,
                    correlation_id=correlation_id,
                    investigation_id=investigation_id,
                    source_id=str(be.event_id),
                    producer_service=settings.service_name,
                    idempotency_key=f"evidence-graph:{identity}:{be.event_id}",
                    source_event_ids=[str(be.event_id)],
                    evidence_graph={"nodes": repo.nodes, "relationships": repo.relationships},
                )
                _publisher.publish(settings.evidence_graph_topic,
                                   graph_event.model_dump_json().encode(),
                                   identity.encode())
                _published_events.add(str(event_id))
        except Exception as exc:
            logger.error("processing_failed", extra={"error": str(exc)})
            raise

    _consumer.start(handler)


@app.on_event("shutdown")
async def shutdown_event():
    global _consumer
    if _consumer:
        _consumer.stop()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.get("/live")
async def live():
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready")
async def ready():
    return {"status": "ready", "service": settings.service_name,
            "consumer_started": bool(_consumer and _consumer._running)}


@app.get("/api/v1/debug/graph")
async def debug_graph():
    # expose nodes, relationships, counts; hide implementation details
    nodes = []
    for cid, v in repo.nodes.items():
        nodes.append({"id": cid, "labels": v.get("labels"), "properties": v.get("properties")})
    rels = repo.relationships
    return {"nodes": nodes, "relationships": rels, "counts": {"nodes": len(nodes), "relationships": len(rels)}}
