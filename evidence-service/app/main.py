from fastapi import FastAPI
from app.core.logger import get_logger
from app.config.settings import settings
from app.repo.inmemory import InMemoryGraphRepo
from app.pipeline.graph_engine import GraphEngine
from app.infrastructure.kafka_client import KafkaConsumerWrapper
from shared.sentineliq_shared.events.base import BaseEvent
from app.pipeline.extractor import extract
from app.pipeline.resolver import resolve_entities
from app.pipeline.relationship_builder import build_relationships

logger = get_logger("main")
app = FastAPI(title="evidence-service")

# in-memory repo used for dev and tests; can be swapped for Neo4j-backed repo later
repo = InMemoryGraphRepo()
engine = GraphEngine(repo)
_consumer = None


@app.on_event("startup")
async def startup_event():
    global _consumer
    logger.info("startup", extra={"service": settings.service_name})

    # start consumer for normalized topic
    _consumer = KafkaConsumerWrapper(settings.normalized_topic)

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
        except Exception as exc:
            logger.error("processing_failed", extra={"error": str(exc)})

    _consumer.start(handler)


@app.on_event("shutdown")
async def shutdown_event():
    global _consumer
    if _consumer:
        _consumer.stop()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.get("/api/v1/debug/graph")
async def debug_graph():
    # expose nodes, relationships, counts; hide implementation details
    nodes = []
    for cid, v in repo.nodes.items():
        nodes.append({"id": cid, "labels": v.get("labels"), "properties": v.get("properties")})
    rels = repo.relationships
    return {"nodes": nodes, "relationships": rels, "counts": {"nodes": len(nodes), "relationships": len(rels)}}
