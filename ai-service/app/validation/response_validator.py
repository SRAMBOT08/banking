from __future__ import annotations
from typing import Any, Dict, List
from app.models.context import AIContext
from app.schemas.api import AIResponse


class ResponseValidationError(ValueError):
    def __init__(self, findings: List[str]):
        self.findings = findings
        super().__init__("AI response rejected: " + ", ".join(findings))


class ResponseValidator:
    def validate(self, response: AIResponse, context: AIContext) -> List[str]:
        findings: List[str] = []
        if response.snapshot_id != context.snapshot_id or response.snapshot_version != context.snapshot_version:
            findings.append("snapshot_reference_mismatch")
        if response.confidence != int(context.confidence.get("score", 0)):
            findings.append("confidence_changed")
        if response.priority != context.priority:
            findings.append("priority_changed")
        evidence_ids = {str(item.get("evidence_id")) for item in context.evidence if item.get("evidence_id")}
        recommendation_ids = {str(item.get("recommendation_id")) for item in context.recommendations if item.get("recommendation_id")}
        hypothesis_ids = {str(item.get("hypothesis_id")) for item in context.hypotheses if item.get("hypothesis_id")}
        for claim in response.claims:
            if not claim.source_ids:
                findings.append("uncited_claim")
            if any(source_id not in evidence_ids and source_id not in hypothesis_ids for source_id in claim.source_ids):
                findings.append("unknown_claim_source")
        for recommendation in response.recommendations:
            identifier = str(recommendation.get("recommendation_id", ""))
            if identifier not in recommendation_ids:
                findings.append("invented_recommendation")
        return sorted(set(findings))

    def assert_valid(self, response: AIResponse, context: AIContext) -> AIResponse:
        findings = self.validate(response, context)
        if findings:
            raise ResponseValidationError(findings)
        return response
