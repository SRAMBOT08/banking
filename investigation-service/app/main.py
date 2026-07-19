from fastapi import FastAPI
from app.config.settings import settings
from app.core.logger import get_logger
from app.api.routes import router, configure
from app.events.kafka import KafkaConsumer, KafkaProducer
from app.pipeline.candidate_consumer import CandidatePipeline
from app.services.investigation_manager import InvestigationManager
from app.services.memory import InvestigationMemory
from app.services.context_builder import InvestigationContextBuilder
from app.services.replay import InvestigationReplay
from app.services.metrics import InvestigationMetricsEngine
from app.services.snapshot_manager import SnapshotManager
from app.repositories import InMemoryInvestigationRepository, InvestigationRepository
from app.database import db_manager
from app.database.schema import initialize_database

logger = get_logger("investigation-service")
app = FastAPI(title=settings.service_name)

# Dependency Injection: Use interface, default to InMemory implementation
# Can be switched to PostgreSQL via configuration
if hasattr(settings, 'database_url') and settings.database_url and not settings.database_url.startswith('sqlite'):
    # PostgreSQL mode - will be initialized on startup
    repository: InvestigationRepository = None  # Will be set in startup
else:
    repository = InMemoryInvestigationRepository()

memory = InvestigationMemory()
manager = InvestigationManager(repository=repository, memory=memory)
context_builder = InvestigationContextBuilder(memory)
replay_engine = InvestigationReplay(memory)
metrics_engine = InvestigationMetricsEngine()
publisher = KafkaProducer()
snapshot_manager = SnapshotManager(memory, on_created=lambda snapshot: publisher.publish_snapshot(settings.snapshot_topic, snapshot))
manager.set_snapshot_manager(snapshot_manager)
consumer = KafkaConsumer(settings.consumer_topic, settings.consumer_group)
configure(manager, context_builder, replay_engine, metrics_engine, publisher, snapshot_manager)
app.include_router(router)


@app.on_event("startup")
async def startup():
    # Initialize database if using PostgreSQL
    global repository
    if repository is None:
        await db_manager.initialize()
        from app.repositories.postgres_repository import PostgresInvestigationRepository
        repository = PostgresInvestigationRepository(db_manager.pool)
    
    await initialize_database()
    consumer.start(CandidatePipeline(manager, publisher, context_builder, snapshot_manager).handle)
    logger.info("service_started", extra={"service": settings.service_name, "consumer_topic": settings.consumer_topic, "producer_topic": settings.producer_topic})


@app.on_event("shutdown")
async def shutdown():
    consumer.stop()
    await db_manager.close()