from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.api.case_routes import create_case_router
from app.config.settings import Settings
from app.events.report_consumer import ReportGeneratedConsumer
from app.events.pipeline import ExecutionPipeline
from app.events.publisher import ExecutionEventPublisher
from app.repositories.inmemory import ExecutionRepository
from app.services.platform import ExecutionPlatformService
from app.repository import CaseExecutionRepository
from app.execution import CaseExecutionService



def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    case_execution_repository = CaseExecutionRepository()
    case_execution_service = CaseExecutionService(case_execution_repository)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository = ExecutionRepository()
        platform = ExecutionPlatformService(config, repository)
        publisher = ExecutionEventPublisher(config)
        pipeline = ExecutionPipeline(platform, publisher)

        consumer = None
        processed_case_versions: set[str] = set()
        if config.kafka_bootstrap:
            async def handle_report(event):
                case_key = f"{event.get('case_id')}:{event.get('case_version')}"
                if case_key in processed_case_versions:
                    return
                await pipeline.handle_report_generated(event)
                processed_case_versions.add(case_key)

            consumer = ReportGeneratedConsumer(config, handle_report)
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
    app.state.case_execution_repository = case_execution_repository
    app.state.case_execution_service = case_execution_service
    app.include_router(create_case_router())
    return app


app = create_app()
