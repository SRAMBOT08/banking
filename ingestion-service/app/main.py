from fastapi import FastAPI

from app.core.logger import get_logger
from app.config.settings import settings
from app.infrastructure.kafka_client import KafkaConsumerWrapper, KafkaProducerWrapper
from app.infrastructure.dedupe import RedisDedupeStore, InMemoryDedupeStore

logger = get_logger("main")

app = FastAPI(title=settings.service_name)

@app.on_event("startup")
async def startup_event():
    logger.info("startup", extra={"service": settings.service_name})

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
