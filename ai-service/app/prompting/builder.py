from __future__ import annotations
import json
from pathlib import Path
from typing import Dict
from app.models.context import AIContext


class PromptBuilder:
    def __init__(self, template_dir: str | None = None):
        self.template_dir = Path(template_dir or Path(__file__).parent / "templates")

    def build(self, context: AIContext, reasoning_type: str, message: str | None = None) -> str:
        template_names = {
            "chat": "chat",
            "technical_summary": "technical",
            "compliance": "compliance",
            "executive_summary": "executive",
            "soc_analyst": "soc_analyst",
            "fraud_team": "fraud_team",
            "incident_response": "incident_response",
            "risk_team": "risk_team",
            "root_cause": "root_cause",
            "evidence_explanation": "evidence_explanation",
            "recommendation": "recommendation",
            "timeline_summary": "timeline_summary",
            "attack_narrative": "attack_narrative",
        }
        template_name = template_names.get(reasoning_type, "executive")
        specialized = (self.template_dir / f"{template_name}.txt").read_text(encoding="utf-8")
        base = (self.template_dir / "base.txt").read_text(encoding="utf-8")
        specialized = specialized.format(message=message or "")
        payload: Dict = {"context": context.model_dump(mode="json"), "specialized_instruction": specialized}
        return base.format(reasoning_type=reasoning_type, context=json.dumps(payload, sort_keys=True, separators=(",", ":")))
