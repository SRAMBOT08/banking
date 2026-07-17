# Deployment Guide

## Purpose
This document provides instructions for deploying the Lokii Platform in development and production environments. It covers prerequisites, Docker Compose setups, startup configurations, networking parameters, and troubleshooting steps.

## Overview
Lokii is packaged as a collection of Docker container services managed via Docker Compose. The platform deploys with Zookeeper, Apache Kafka, PostgreSQL, Neo4j, Redis, and individual FastAPI backend services, connecting the Next.js visual dashboard through a unified Gateway.

---

## Detailed Explanation

### 1. Prerequisites
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Resources**: Minimum 8GB RAM, 4 CPU cores (16GB RAM recommended for full stack run).

### 2. Multi-Stage Dockerfiles
Backend Python services share the monolithic SDK module inside the `/shared` folder. During build execution, Docker mounts the local project directory and installs the shared library:
```dockerfile
COPY shared /shared
RUN pip install -e /shared
```

### 3. Startup Order
To prevent database connection errors during startup, services launch in a controlled sequence:
1. **Core Brokers**: `zookeeper` and `kafka`.
2. **Databases**: `postgres`, `neo4j`, and `redis`.
3. **Core Services**: `investigation-service`, `evidence-service`, and `threat-intelligence-service`.
4. **API Gateway**: `gateway`.
5. **UI & Consumers**: `frontend` and `test-runner`.

### 4. Health Checks
FastAPI containers use curl or python checks inside their definitions to delay downstream startup until health endpoints report ready:
```yaml
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')\""]
  interval: 10s
  timeout: 5s
  retries: 12
```

---

## Workflow

### Local Deployment Quickstart
1. **Setup Env**: Copy variables from the example configuration:
   ```bash
   cp .env.example .env
   ```
2. **Launch Stack**: Build and start the docker compose services in the background:
   ```bash
   docker compose up -d --build
   ```
3. **Verify Health**: Poll the central health aggregation route:
   ```bash
   curl http://localhost:8000/api/v1/platform/health
   ```
4. **Open UI**: Open your browser and navigate to `http://localhost:3000`.

---

## Design Decisions
- **Private Bridge Network (`sentinel_net`)**: Isolates service communications, exposing only Gateway (`8000`) and Frontend (`3000`) ports to the host machine.
- **Named Data Volumes**: Persist state across container restarts:
  ```yaml
  volumes:
    postgres_data:
    neo4j_data:
    redis_data:
    kafka_data:
  ```

## Best Practices
- **Never Hardcode Secrets**: Store database credentials and API tokens in the local `.env` file instead of committing them to Dockerfiles.
- **Set Up Memory Limits**: Assign resource limitations (CPU/Memory constraints) to containers in production compose definitions.

## Future Enhancements
- Export configurations to Helm Charts for deployment to Kubernetes clusters.
- Configure SSL certificates at the Gateway level to protect HTTP traffic.
