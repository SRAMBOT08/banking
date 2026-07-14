from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.config.settings import Settings
from app.events.kafka import KafkaPublisher, SnapshotEventConsumer
from app.memory.conversation import ConversationMemory
from app.pipeline.snapshot_pipeline import SnapshotPipeline
from app.prompting.builder import PromptBuilder
from app.providers.factory import LLMProviderFactory
from app.reasoning.engine import ReasoningEngine
from app.services.ai_service import AIInvestigationService
from app.services.cache import InMemoryCache
from app.services.context_loader import SnapshotContextLoader
from app.services.metrics import AIMetrics
from app.services.snapshot_client import InvestigationSnapshotClient
from app.validation.response_validator import ResponseValidator


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        provider = LLMProviderFactory.create(config)
        metrics = AIMetrics()
        cache = InMemoryCache()
        conversation = ConversationMemory()
        service = AIInvestigationService(SnapshotContextLoader(), PromptBuilder(),
                                         ReasoningEngine(provider, PromptBuilder(), ResponseValidator()),
                                         conversation, metrics, cache, config)
        publisher = KafkaPublisher(config) if config.kafka_bootstrap else None
        snapshot_client = InvestigationSnapshotClient(config)
        pipeline = SnapshotPipeline(snapshot_client, service, publisher)
        consumer = None
        if config.kafka_bootstrap:
            consumer = SnapshotEventConsumer(config, pipeline.handle)
            consumer.start()
        app.state.settings = config
        app.state.provider = provider
        app.state.metrics = metrics
        app.state.cache = cache
        app.state.conversation = conversation
        app.state.service = service
        app.state.snapshot_client = snapshot_client
        app.state.consumer = consumer
        yield
        if consumer:
            await consumer.stop()

    app = FastAPI(title="AI Investigation Service", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
