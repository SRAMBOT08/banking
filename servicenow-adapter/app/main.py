from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.audit.store import ImmutableAuditStore
from app.auth.providers import BasicAuthProvider
from app.client.rest_client import ServiceNowRestClient
from app.config import AdapterSettings
from app.events.kafka import AdapterEventPublisher, ReadyTaskConsumer
from app.health.service import HealthService
from app.mapper.servicenow_mapper import ServiceNowTaskMapper
from app.models import RetryPolicy
from app.operations.change.service import ChangeOperationService
from app.operations.cmdb.service import CmdbOperationService
from app.operations.incident.service import IncidentOperationService
from app.operations.user.service import UserOperationService
from app.retry.engine import RetryEngine
from app.service import ServiceNowAdapterService
from app.verification.incident_verifier import IncidentVerifier


def create_app(settings: AdapterSettings | None = None) -> FastAPI:
    config = settings or AdapterSettings()

    auth = BasicAuthProvider.from_settings(config)
    retry_policy = RetryPolicy(
        max_retries=config.max_retry_count,
        base_delay_ms=config.retry_base_delay_ms,
        max_delay_ms=config.retry_max_delay_ms,
    )
    retry_engine = RetryEngine(retry_policy)
    client = ServiceNowRestClient(config, auth.auth_tuple(), retry_engine)
    mapper = ServiceNowTaskMapper()
    incident_ops = IncidentOperationService(client, mapper)
    user_ops = UserOperationService(client, mapper)
    cmdb_ops = CmdbOperationService(client, mapper)
    change_ops = ChangeOperationService(client, mapper)
    verifier = IncidentVerifier(client)
    audit_store = ImmutableAuditStore(config.audit_log_path)
    publisher = AdapterEventPublisher(config)
    adapter_service = ServiceNowAdapterService(
        incident_ops,
        user_ops,
        cmdb_ops,
        change_ops,
        verifier,
        mapper,
        audit_store,
        publisher,
        config.log_level,
    )
    health_service = HealthService(config, client)
    consumer = ReadyTaskConsumer(config, adapter_service.process_event) if config.kafka_bootstrap_servers else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if consumer:
            consumer.start()
        yield
        if consumer:
            await consumer.stop()
        await client.close()

    app = FastAPI(title="ServiceNow Execution Adapter", lifespan=lifespan)
    app.state.settings = config
    app.state.client = client
    app.state.adapter_service = adapter_service
    app.state.health_service = health_service
    app.state.consumer = consumer
    app.include_router(router)
    return app


app = create_app()
