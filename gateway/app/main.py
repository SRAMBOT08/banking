from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from app.core.logger import get_logger
from app.config.settings import settings
from app.infrastructure.kafka_client import KafkaProducerWrapper

from shared.sentineliq_shared.events.base import BaseEvent
from app.api.proxy_routes import router as proxy_router

logger = get_logger("gateway")

app = FastAPI(title="SentinelIQ Gateway")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.post("/api/v1/debug/publish-event")
async def publish_event(request: Request):
    """Receive JSON (or scenario) and publish to Kafka using configured routing."""
    payload = await request.json()
    producer = KafkaProducerWrapper()

    # built-in scenario
    if isinstance(payload, dict) and payload.get("scenario") == "account_takeover":
        tenant_id = payload.get("tenant_id", "tenant-001")
        correlation_id = payload.get("correlation_id", "22222222-2222-2222-2222-222222222222")
        investigation_id = payload.get("investigation_id", "33333333-3333-3333-3333-333333333333")

        # deterministic events
        events = []
        base_ts = "2024-01-01T00:00:00Z"
        # 1 Successful Login
        events.append({
            "event_id": "11111111-1111-1111-1111-111111111111",
            "event_type": "authentication",
            "event_version": "1.0.0",
            "timestamp": base_ts,
            "ingestion_timestamp": base_ts,
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "tenant_id": tenant_id,
            "source_id": "gateway",
            "producer_service": "gateway",
            "schema_version": "1.0",
            "metadata": {"user_id": "user-42", "ip": "203.0.113.5"},
        })
        # 2 New Device Registration
        events.append({
            "event_id": "11111111-1111-1111-1111-111111111112",
            "event_type": "asset",
            "event_version": "1.0.0",
            "timestamp": base_ts,
            "ingestion_timestamp": base_ts,
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "tenant_id": tenant_id,
            "source_id": "gateway",
            "producer_service": "gateway",
            "schema_version": "1.0",
            "metadata": {"device_id": "device-900", "user_id": "user-42"},
        })
        # 3 VPN Login
        events.append({
            "event_id": "11111111-1111-1111-1111-111111111113",
            "event_type": "authentication",
            "event_version": "1.0.0",
            "timestamp": base_ts,
            "ingestion_timestamp": base_ts,
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "tenant_id": tenant_id,
            "source_id": "gateway",
            "producer_service": "gateway",
            "schema_version": "1.0",
            "metadata": {"user_id": "user-42", "ip": "198.51.100.7", "vpn": True},
        })
        # 4 Beneficiary Added
        events.append({
            "event_id": "11111111-1111-1111-1111-111111111114",
            "event_type": "transaction",
            "event_version": "1.0.0",
            "timestamp": base_ts,
            "ingestion_timestamp": base_ts,
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "tenant_id": tenant_id,
            "source_id": "gateway",
            "producer_service": "gateway",
            "schema_version": "1.0",
            "metadata": {"beneficiary_id": "ben-55", "account_id": "acct-1234", "user_id": "user-42"},
        })
        # 5 Large Transaction
        events.append({
            "event_id": "11111111-1111-1111-1111-111111111115",
            "event_type": "transaction",
            "event_version": "1.0.0",
            "timestamp": base_ts,
            "ingestion_timestamp": base_ts,
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "tenant_id": tenant_id,
            "source_id": "gateway",
            "producer_service": "gateway",
            "schema_version": "1.0",
            "metadata": {"transaction_id": "txn-9999", "amount": 100000.0, "currency": "USD", "account_id": "acct-1234"},
        })

        published = []
        for ev in events:
            try:
                be = BaseEvent.model_validate(ev)
            except Exception as e:
                logger.error("validation_failed_local", extra={"error": str(e), "event": ev.get("event_id")})
                raise HTTPException(status_code=400, detail=str(e))

            topic = settings.topic_map.get(be.event_type, settings.topic_map.get("default"))
            producer.produce(topic, key=str(be.event_id).encode(), value=be.model_dump_json().encode())
            logger.info("published_event", extra={"event_id": str(be.event_id), "topic": topic, "correlation_id": str(be.correlation_id), "trace_id": str(be.trace_id), "tenant_id": be.tenant_id})
            published.append({"event_id": str(be.event_id), "topic": topic})

        producer.flush()
        return {"status": "published_scenario", "published": published}

    # single event path
    try:
        # accept raw JSON and validate into BaseEvent
        be = BaseEvent.model_validate(payload)
    except Exception as exc:
        logger.error("validation_failed_local", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))

    topic = settings.topic_map.get(be.event_type, settings.topic_map.get("default"))
    producer.produce(topic, key=str(be.event_id).encode(), value=be.model_dump_json().encode())
    producer.flush()

    logger.info("published_event", extra={"event_id": str(be.event_id), "topic": topic, "correlation_id": str(be.correlation_id), "trace_id": str(be.trace_id), "tenant_id": be.tenant_id})

    return {"status": "published", "event_id": str(be.event_id), "topic": topic}


@app.get("/api/v1/debug/graph")
async def proxy_graph():
    # proxy to evidence-service debug endpoint
    url = "http://evidence-service:8200/api/v1/debug/graph"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=10.0)
            r.raise_for_status()
        except Exception as exc:
            # return a helpful error
            raise HTTPException(status_code=502, detail=f"failed to contact evidence-service: {exc}")
    return r.json()
