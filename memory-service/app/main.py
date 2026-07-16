from __future__ import annotations

from fastapi import FastAPI
from .api.query_routes import create_query_router
from .query.in_memory import InMemoryInvestigationMemoryRepository
from .query.service import InvestigationMemoryQueryService


def create_app(repository=None) -> FastAPI:
    repository = repository or InMemoryInvestigationMemoryRepository()
    service = InvestigationMemoryQueryService(repository)
    app = FastAPI(title="SentinelIQ Investigation Memory Service", version="1.0.0")
    app.include_router(create_query_router(service))

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "investigation-memory", "repository": service.metadata().repository}

    return app


app = create_app()
