# Enterprise Event Simulator Service

The simulator is a production-grade cyber-range telemetry producer for SentinelIQ. It creates deterministic or continuously scheduled enterprise banking activity, embeds attack timelines in realistic background noise, and publishes contract-shaped telemetry to `events.unified.v1` for ingestion.

## Responsibilities

- Generate realistic banking identities, devices, locations, networks, sessions, authentication, endpoint, email, cloud, and transaction telemetry.
- Compose all supported attack scenarios into chronological timelines.
- Mutate scenarios with controlled variation while preserving causal relationships.
- Support deterministic replay through a seed and independent or concurrent scenario runs.
- Publish to Kafka or retain events in memory for local development.

## API

- `GET /health`
- `GET /scenarios`
- `POST /simulations` — start one or more scenarios.
- `GET /simulations/{id}` — inspect status and counters.
- `POST /simulations/{id}/stop`
- `GET /simulations/{id}/events` — inspect generated events.

## Configuration

`KAFKA_BOOTSTRAP_SERVERS` defaults to `localhost:9092`; `EVENT_TOPIC` defaults to `events.unified.v1`; `SIMULATOR_TRANSPORT` may be `kafka` or `memory`.
