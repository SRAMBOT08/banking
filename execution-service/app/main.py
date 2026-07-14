from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.settings import Settings
from app.events.kafka import CompletedInvestigationConsumer
from app.events.pipeline import ExecutionPipeline
from app.events.publisher import ExecutionEventPublisher
from app.repositories.inmemory import ExecutionRepository
from app.services.platform import ExecutionPlatformService



def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository = ExecutionRepository()
        platform = ExecutionPlatformService(config, repository)
        publisher = ExecutionEventPublisher(config)
        pipeline = ExecutionPipeline(platform, publisher)

        consumer = None
        if config.kafka_bootstrap:
            consumer = CompletedInvestigationConsumer(config, pipeline.handle_completed_investigation)
            consumer.start()

        app.state.settings = config
        app.state.repository = repository
        app.state.platform = platform
        app.state.publisher = publisher
        app.state.pipeline = pipeline
        app.state.consumer = consumer
        yield
        if consumer:
            await consumer.stop()

    app = FastAPI(title="Execution Decision & Orchestration Service", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
