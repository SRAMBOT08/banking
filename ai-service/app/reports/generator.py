from __future__ import annotations
from typing import Any, Dict
from app.models.context import AIContext
from app.schemas.api import ReportResponse


class ReportGenerator:
    def generate(self, context: AIContext, report_type: str = "executive", output_format: str = "json") -> ReportResponse:
        title = f"SentinelIQ {report_type.title()} Investigation Report"
        sections = {
            "summary": {
                "snapshot_id": context.snapshot_id,
                "snapshot_version": context.snapshot_version,
                "investigation_id": context.investigation.get("investigation_id"),
                "priority": context.priority,
                "confidence": context.confidence.get("score", 0),
            },
            "known_facts": [item.get("evidence_id") for item in context.evidence],
            "hypotheses": [item.get("hypothesis_id") for item in context.hypotheses],
            "missing_evidence": list(context.missing_evidence),
            "recommendations": list(context.recommendations),
        }
        return ReportResponse(report_type=report_type, format=output_format, snapshot_id=context.snapshot_id,
                              snapshot_version=context.snapshot_version, title=title, sections=sections,
                              traceability=[context.snapshot_id], model="deterministic-report-generator")
