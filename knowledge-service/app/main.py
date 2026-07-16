from fastapi import FastAPI
from app.api.query_routes import create_query_router
from app.query.in_memory import InMemoryKnowledgeRepository
from app.query.service import KnowledgeQueryService


repository = InMemoryKnowledgeRepository()
query_service = KnowledgeQueryService(repository)
app = FastAPI(title="SentinelIQ Enterprise Knowledge Platform")
app.include_router(create_query_router(query_service))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "knowledge-service"}
