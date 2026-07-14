# SentinelIQ

AI-powered Evidence Intelligence and Decision Platform for Banking Security.

This repository is a production-grade engineering foundation for SentinelIQ — an event-driven, microservices platform designed to ingest telemetry, build evidence graphs, and support AI-assisted investigations.

## SentinelIQ (Cohort_Web_App)

Docker-first developer workflow

1. git clone <repo>
2. docker compose up --build
3. (optional) docker compose --profile test up

This repository is Docker-first: services are built inside containers and the `shared/` package is installed into service images during build. Developers do not need to run `pip install` locally.

# Cohort_Web_App
See `docs/` for architecture and development guidelines.
