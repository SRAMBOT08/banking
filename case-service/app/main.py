import os
from fastapi import FastAPI
from .api import create_api_router
from .builder import CaseBuilder
from .events import CaseEventPublisher, CompletedInvestigationConsumer, case_event
from .query.router import create_query_router
from .query.service import CaseQueryService
from .repository import InMemoryCaseRepository

repository = InMemoryCaseRepository()
builder = CaseBuilder(repository)
query_service = CaseQueryService(repository)
app = FastAPI(title='SentinelIQ Enterprise Case Builder', version='1.0.0')
app.include_router(create_api_router(builder))
app.include_router(create_query_router(query_service))
_consumer = None


@app.on_event('startup')
async def start_event_consumer():
	global _consumer
	bootstrap = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
	if not bootstrap:
		return
	input_topic = os.getenv('INVESTIGATION_COMPLETED_TOPIC', 'investigation.completed.v1')
	output_topic = os.getenv('CASE_CREATED_TOPIC', 'case.created.v1')
	publisher = CaseEventPublisher(bootstrap, output_topic)

	async def handle(event):
		context = event.context or event.snapshot
		case_file = builder.build(context, created_by='case-service')
		publisher.publish(case_event(case_file, event, 'case-service'))

	_consumer = CompletedInvestigationConsumer(
		bootstrap, input_topic, os.getenv('CASE_CONSUMER_GROUP', 'case-service-group'),
		os.getenv('CASE_DLQ_TOPIC', 'investigation.completed.dlq.v1'), handle,
	)
	_consumer.start()


@app.on_event('shutdown')
async def stop_event_consumer():
	if _consumer:
		await _consumer.stop()


@app.get('/health')
async def health(): return {'status': 'ok', 'service': 'case-service'}


@app.get('/live')
async def live(): return {'status': 'ok', 'service': 'case-service'}


@app.get('/ready')
async def ready():
	return {'status': 'ready', 'service': 'case-service', 'consumer_started': bool(_consumer and _consumer.running)}
