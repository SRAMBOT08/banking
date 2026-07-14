from fastapi import FastAPI

from app.core.logger import get_logger
from app.config.settings import settings
from app.infrastructure.kafka_client import KafkaConsumerWrapper, KafkaProducerWrapper
from app.infrastructure.dedupe import RedisDedupeStore, InMemoryDedupeStore
from app.pipeline.orchestrator import PipelineOrchestrator
from app.pipeline.publisher import Publisher
from app.pipeline.deduper import Deduper

_consumers = []


logger = get_logger("main")

app = FastAPI(title=settings.service_name)

@app.on_event("startup")
async def startup_event():
    logger.info("startup", extra={"service": settings.service_name})

    # choose a dedupe store
    try:
        store = RedisDedupeStore(str(settings.redis_url))
    except Exception:
        store = InMemoryDedupeStore()

    orchestrator = PipelineOrchestrator(Deduper(store), Publisher())

    # subscribe to ingress topics
    for topic in settings.ingress_topics:
        consumer = KafkaConsumerWrapper(topic, group_id=settings.kafka_group_id)

        async def _handler(msg, _orchestrator=orchestrator):
            try:
                raw = msg.value()
                await _orchestrator.handle_message(raw)
            except Exception as exc:
                logger.error("orchestrator_error", extra={"error": str(exc)})

        consumer.start(_handler)
        _consumers.append(consumer)

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.on_event("shutdown")
async def shutdown_event():
    for c in _consumers:
        try:
            c.stop()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
