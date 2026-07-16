# Enterprise Case Builder Service

The Case Builder transforms a completed `InvestigationContext` into the immutable, versioned SentinelIQ `CaseFile`. It is a packaging and record service only: it does not call intelligence services, reason, calculate confidence, make decisions, invoke LLMs, or execute actions.

## API

- `GET /health`
- `POST /api/v1/cases/build`
- `GET /api/v1/cases/{id}`
- `GET /api/v1/cases/{id}/versions`
- `GET /api/v1/cases/{id}/history`
- `GET /api/v1/cases/{id}/audit`
- `GET /api/v1/cases/{id}/timeline`
- `GET /api/v1/cases/statistics`
- `GET /api/v1/cases/search`

The default repository is in-memory and is hidden behind repository interfaces. It can be replaced by a durable implementation without changing builders, query services, or controllers.
