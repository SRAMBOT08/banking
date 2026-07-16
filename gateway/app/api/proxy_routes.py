from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.core.logger import get_logger
from app.infrastructure.kafka_client import KafkaProducerWrapper

router = APIRouter(prefix="/api/v1", tags=["gateway-proxy"])
logger = get_logger("gateway_proxy")


class ScenarioRequest(BaseModel):
    scenario: str = Field(min_length=1)
    tenant_id: str = "demo-bank"
    seed: int = 1


def _scenario_title(scenario: str) -> str:
    return scenario.replace("_", " ").title()


def _demo_candidate_payload(simulation_id: str, scenario: str, tenant_id: str, seed: int) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    scenario_key = scenario.strip().lower().replace(" ", "_")
    candidate_id = f"demo-candidate-{simulation_id}"
    correlation_id = str(uuid5(NAMESPACE_URL, f"correlation|{simulation_id}|{seed}"))
    default_indicators = ["new_device", "high_risk_authentication", "anomalous_transaction"]
    scenario_indicators = {
        "account_takeover": ["impossible_mfa", "new_device", "large_transfer"],
        "credential_stuffing": ["repeated_login_failure", "distributed_source_ips", "velocity_spike"],
        "password_spray": ["password_spray_pattern", "multi_account_targeting", "auth_failure_burst"],
        "money_mule": ["new_beneficiary", "rapid_transfer_chain", "account_linkage"],
        "insider_threat": ["privileged_access", "policy_deviation", "suspicious_export"],
        "ransomware": ["malicious_execution", "lateral_movement", "encryption_activity"],
    }
    matched_indicators = scenario_indicators.get(scenario_key, default_indicators)
    evidence_refs = [
        {"evidence_id": f"{simulation_id}-auth", "type": "authentication_event"},
        {"evidence_id": f"{simulation_id}-device", "type": "device_change"},
        {"evidence_id": f"{simulation_id}-transfer", "type": "large_transfer"},
    ]
    return {
        "candidate_id": candidate_id,
        "investigation_id": simulation_id,
        "correlation_id": correlation_id,
        "tenant_id": tenant_id,
        "pattern_name": _scenario_title(scenario_key),
        "pattern_version": "1.0.0",
        "confidence": 94 if scenario_key == "account_takeover" else 88,
        "explanation": {
            "summary": f"Deterministic demo candidate generated for {scenario_key}.",
            "source": "gateway-demo-bridge",
            "simulation_id": simulation_id,
            "seed": seed,
        },
        "evidence_refs": evidence_refs,
        "timestamp": timestamp,
        "matched_indicators": matched_indicators,
        "missing_indicators": [],
    }


def _publish_demo_candidate(simulation_id: str, scenario: str, tenant_id: str, seed: int) -> None:
    candidate = _demo_candidate_payload(simulation_id, scenario, tenant_id, seed)
    producer = KafkaProducerWrapper()
    producer.produce(
        "investigation.candidates.v1",
        key=candidate["candidate_id"].encode(),
        value=json.dumps(candidate).encode(),
    )
    producer.flush()
    logger.info(
        "demo_candidate_published",
        extra={
            "candidate_id": candidate["candidate_id"],
            "simulation_id": simulation_id,
            "scenario": scenario,
        },
    )


async def forward(method: str, url: str, **kwargs: Any) -> Any:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
            response = await client.request(method, url, **kwargs)
        if response.status_code >= 400:
            detail = response.text[:500] or "upstream service error"
            raise HTTPException(response.status_code, detail)
        return response.json()
    except HTTPException:
        raise
    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        raise HTTPException(502, f"upstream unavailable: {exc}") from exc


@router.get("/investigations")
async def investigations():
    return await forward("GET", f"{settings.investigation_service_url}/investigations")


@router.get("/investigations/{investigation_id}")
async def investigation(investigation_id: str):
    return await forward("GET", f"{settings.investigation_service_url}/investigations/{investigation_id}")


@router.get("/investigations/{investigation_id}/context")
async def investigation_context(investigation_id: str):
    return await forward("GET", f"{settings.investigation_service_url}/investigations/{investigation_id}/context")


@router.get("/investigations/{investigation_id}/timeline")
async def investigation_timeline(investigation_id: str):
    return await forward("GET", f"{settings.investigation_service_url}/investigations/{investigation_id}/timeline")


@router.get("/investigations/{investigation_id}/memory")
async def investigation_memory(investigation_id: str):
    return await forward("GET", f"{settings.investigation_service_url}/investigations/{investigation_id}/memory")


@router.get("/investigations/{investigation_id}/graph")
async def investigation_graph(investigation_id: str):
    return await forward("GET", f"{settings.investigation_service_url}/investigations/{investigation_id}/graph")


@router.get("/investigations/{investigation_id}/reports")
async def investigation_reports(investigation_id: str):
    return await forward("GET", f"{settings.report_service_url}/api/v1/reports/search", params={"case_id": investigation_id})


@router.get("/cases/{case_id}")
async def case(case_id: UUID):
    return await forward("GET", f"{settings.case_service_url}/api/v1/cases/{case_id}")


@router.get("/cases/{case_id}/timeline")
async def case_timeline(case_id: UUID):
    return await forward("GET", f"{settings.case_service_url}/api/v1/cases/{case_id}/timeline")


@router.get("/cases/{case_id}/audit")
async def case_audit(case_id: UUID):
    return await forward("GET", f"{settings.case_service_url}/api/v1/cases/{case_id}/audit")


@router.get("/reports/{report_id}")
async def report(report_id: UUID):
    return await forward("GET", f"{settings.report_service_url}/api/v1/reports/{report_id}")


@router.get("/executions/status")
async def execution_status():
    return await forward("GET", f"{settings.execution_service_url}/execution/status")


@router.get("/executions/history")
async def execution_history():
    return await forward("GET", f"{settings.execution_service_url}/api/v1/executions/history")


@router.get("/graph/investigation/{investigation_id}")
async def graph_investigation(investigation_id: str):
    return await forward("GET", f"{settings.graph_service_url}/api/v1/graph/investigation/{investigation_id}")


@router.post("/simulations/run", status_code=202)
async def run_scenario(request: ScenarioRequest):
    scenario = request.scenario.strip().lower().replace(" ", "_")
    response = await forward("POST", f"{settings.simulator_service_url}/simulations", json={
        "scenarios": [scenario], "tenant_id": request.tenant_id, "seed": request.seed,
    })
    simulation_id = response.get("simulation_id")
    if simulation_id:
        try:
            _publish_demo_candidate(simulation_id, scenario, request.tenant_id, request.seed)
            response["demo_candidate_status"] = "published"
        except Exception as exc:
            logger.error("demo_candidate_publish_failed", extra={"error": str(exc), "scenario": scenario, "simulation_id": simulation_id})
            response["demo_candidate_status"] = f"failed: {exc}"
    return response


@router.get("/simulations/{simulation_id}")
async def simulation(simulation_id: UUID):
    return await forward("GET", f"{settings.simulator_service_url}/simulations/{simulation_id}")


@router.get("/simulations/{simulation_id}/events")
async def simulation_events(simulation_id: UUID):
    return await forward("GET", f"{settings.simulator_service_url}/simulations/{simulation_id}/events")


@router.get("/platform/health")
async def platform_health():
    services = {
        "gateway": "http://gateway:8000/health",
        "event-simulator": f"{settings.simulator_service_url}/health",
        "investigation": f"{settings.investigation_service_url}/health",
        "case-builder": f"{settings.case_service_url}/health",
        "ai-report": f"{settings.report_service_url}/health",
        "execution": f"{settings.execution_service_url}/health",
        "servicenow": f"{settings.servicenow_service_url}/health",
    }

    async def check(name: str, url: str) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                response = await client.get(url)
            return {"service": name, "status": "healthy" if response.is_success else "degraded", "latency_ms": round(response.elapsed.total_seconds() * 1000, 1), "detail": response.json()}
        except Exception as exc:
            return {"service": name, "status": "offline", "latency_ms": None, "detail": str(exc)}

    return {"services": await asyncio.gather(*(check(name, url) for name, url in services.items()))}
