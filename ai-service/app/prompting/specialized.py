from __future__ import annotations
from app.models.context import AIContext
from app.prompting.builder import PromptBuilder


class SpecializedPromptBuilder:
    reasoning_type = "executive_summary"

    def __init__(self, builder: PromptBuilder | None = None):
        self.builder = builder or PromptBuilder()

    def build(self, context: AIContext, message: str | None = None) -> str:
        return self.builder.build(context, self.reasoning_type, message)


class SOCAnalystPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "soc_analyst"


class ExecutivePromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "executive_summary"


class CompliancePromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "compliance"


class FraudTeamPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "fraud_team"


class IncidentResponsePromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "incident_response"


class RiskTeamPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "risk_team"


class RootCauseAnalysisPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "root_cause"


class EvidenceExplanationPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "evidence_explanation"


class RecommendationPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "recommendation"


class TimelineSummaryPromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "timeline_summary"


class AttackNarrativePromptBuilder(SpecializedPromptBuilder):
    reasoning_type = "attack_narrative"


__all__ = [
    "SpecializedPromptBuilder", "SOCAnalystPromptBuilder", "ExecutivePromptBuilder",
    "CompliancePromptBuilder", "FraudTeamPromptBuilder", "IncidentResponsePromptBuilder",
    "RiskTeamPromptBuilder", "RootCauseAnalysisPromptBuilder", "EvidenceExplanationPromptBuilder",
    "RecommendationPromptBuilder", "TimelineSummaryPromptBuilder", "AttackNarrativePromptBuilder",
]
