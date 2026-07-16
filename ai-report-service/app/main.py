import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import SecretStr
from .api.router import create_router
from .providers import DeterministicNIMProvider, NIMProvider
from .query import ReportQueryService
from .repository import InMemoryReportRepository
from .service import ReportService
from .events import CaseCreatedConsumer, ReportEventPublisher, report_event
from .models import ReportRequest, ReportType, ReportFormat


def create_app(provider=None) -> FastAPI:
    repository = InMemoryReportRepository()
    if provider is None and os.getenv('REPORT_PROVIDER', 'mock').lower() == 'nim':
        api_key = os.getenv('NIM_API_KEY')
        provider = NIMProvider(
            os.getenv('NIM_ENDPOINT', 'http://localhost:8000/v1/chat/completions'),
            os.getenv('NIM_MODEL', 'meta/llama-3.1-70b-instruct'),
            SecretStr(api_key) if api_key else None,
            timeout=float(os.getenv('NIM_TIMEOUT_SECONDS', '30')),
        )
    provider = provider or DeterministicNIMProvider()
    service = ReportService(repository, provider)
    consumer = None
    processed: set[str] = set()

    @asynccontextmanager
    async def lifespan(application):
        nonlocal consumer
        bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
        if bootstrap:
            publisher = ReportEventPublisher(bootstrap, os.getenv('REPORT_GENERATED_TOPIC', 'report.generated.v1'))
            report_types = (
                ReportType.EXECUTIVE, ReportType.TECHNICAL, ReportType.SOC,
                ReportType.TIMELINE, ReportType.MITRE, ReportType.BUSINESS_IMPACT,
                ReportType.ROOT_CAUSE, ReportType.RECOMMENDATIONS,
            )

            async def handle(event):
                if str(event.event_id) in processed:
                    return
                for report_type in report_types:
                    report = await service.generate(ReportRequest(
                        case_file=event.case_file,
                        report_type=report_type,
                        output_format=ReportFormat.JSON,
                        created_by='ai-report-service',
                    ))
                    publisher.publish(report_event(report, event, 'ai-report-service'))
                processed.add(str(event.event_id))

            consumer = CaseCreatedConsumer(
                bootstrap, os.getenv('CASE_CREATED_TOPIC', 'case.created.v1'),
                os.getenv('REPORT_CONSUMER_GROUP', 'ai-report-service-group'),
                os.getenv('REPORT_DLQ_TOPIC', 'case.created.dlq.v1'), handle,
            )
            consumer.start()
        application.state.consumer = consumer
        yield
        if consumer:
            await consumer.stop()

    app = FastAPI(title='SentinelIQ AI Report Service', version='1.0.0', lifespan=lifespan)
    app.state.repository, app.state.service = repository, service
    app.include_router(create_router(service, ReportQueryService(repository)))
    @app.get('/health')
    async def health(): return {'status': 'ok', 'service': 'ai-report-service', 'model': provider.model_name}
    @app.get('/live')
    async def live(): return {'status': 'ok', 'service': 'ai-report-service'}
    @app.get('/ready')
    async def ready(): return {'status': 'ready', 'service': 'ai-report-service', 'consumer_started': bool(consumer and consumer.running)}
    return app


app = create_app()
