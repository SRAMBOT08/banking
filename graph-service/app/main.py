from __future__ import annotations

from fastapi import FastAPI
from .api.query_routes import create_query_router
from .query.in_memory import InMemoryGraphRepository
from .query.service import GraphQueryService


def create_app(repository=None) -> FastAPI:
    repository = repository or InMemoryGraphRepository()
    service = GraphQueryService(repository)
    app = FastAPI(title="SentinelIQ Graph Intelligence Service", version="1.0.0")
    app.include_router(create_query_router(service))

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "graph-intelligence", "repository": service.metadata().repository}

    return app


app = create_app()
