from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class ReportType(StrEnum):
    EXECUTIVE = 'executive_summary'
    TECHNICAL = 'technical_investigation'
    SOC = 'soc_analyst'
    ROOT_CAUSE = 'root_cause_analysis'
    TIMELINE = 'timeline_narrative'
    MITRE = 'mitre_attack_explanation'
    FRAUD = 'fraud_analysis'
    BUSINESS_IMPACT = 'business_impact_summary'
    RECOMMENDATIONS = 'recommendation_report'
    COMPLIANCE = 'compliance_summary'


class ReportFormat(StrEnum):
    MARKDOWN = 'markdown'
    HTML = 'html'
    JSON = 'json'
    PDF_READY = 'pdf_ready'


class ReportRequest(BaseModel):
    case_file: dict[str, Any]
    report_type: ReportType = ReportType.EXECUTIVE
    output_format: ReportFormat = ReportFormat.JSON
    created_by: str = Field(default='system', min_length=1)


class ReportFile(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')
    report_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    case_version: int
    report_type: ReportType
    output_format: ReportFormat
    title: str
    content: str
    structured_content: dict[str, Any]
    model: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    source_hash: str
    provenance: tuple[dict[str, Any], ...] = ()
