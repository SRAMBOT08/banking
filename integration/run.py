from __future__ import annotations
import json
from pathlib import Path
from .harness import run_scenario
from app.models import ScenarioName

SCENARIOS = (ScenarioName.CREDENTIAL_STUFFING, ScenarioName.ACCOUNT_TAKEOVER, ScenarioName.MONEY_MULE, ScenarioName.INSIDER_THREAT, ScenarioName.RANSOMWARE)

if __name__ == '__main__':
    results = [run_scenario(scenario, seed=2026) for scenario in SCENARIOS]
    print(json.dumps([{'scenario': item.scenario, 'case_id': item.case_id, 'report_id': item.report_id, 'execution_id': item.execution_id, 'service_now_ticket': item.service_now_ticket, 'stages': len(item.stages), 'latency_ms': round(sum(stage.latency_ms for stage in item.stages), 3)} for item in results], indent=2))
