"""Payload construction for the ServiceNow pipeline.

This module performs deterministic transformation from the internal
``IncidentRequest`` model to the normalized ``IncidentPayload`` model.
It does not perform lookups, HTTP calls, authentication, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from plugins.servicenow_pipeline.models import IncidentPayload, IncidentRequest
from plugins.servicenow_pipeline.tracing import elapsed_ms, log_stage, new_correlation_id, now, sanitize_payload


@dataclass(slots=True)
class PayloadBuilder:
    """Pure transformation layer for ServiceNow payload normalization."""

    default_table: str = "incident"

    def build_incident_payload(
        self,
        request: IncidentRequest,
        *,
        correlation_id: str | None = None,
    ) -> IncidentPayload:
        """Convert an incident request into a normalized ServiceNow payload.

        The builder keeps reference fields as human-readable values. It does not
        resolve sys_ids or perform any other lookup-based enrichment.
        """
        corr_id = correlation_id or new_correlation_id()
        start = now()
        payload = IncidentPayload(
            table=self.default_table,
            short_description=str(request.short_description).strip(),
            description=str(request.description).strip(),
            priority=self.normalize_priority(request.priority),
            urgency=self.normalize_urgency(request.urgency),
            impact=self.normalize_impact(request.impact),
            category=self.normalize_category(request.category),
            assignment_group=self._normalize_text(request.assignment_group),
            caller=self._normalize_text(request.caller),
        )
        log_stage(
            logger,
            stage="payload_builder",
            correlation_id=corr_id,
            success=True,
            duration_ms=elapsed_ms(start),
            extra={"payload": sanitize_payload(payload)},
        )
        return payload

    def normalize_priority(self, priority: Optional[str]) -> Optional[str]:
        """Normalize priority into a stable string representation."""
        return self._normalize_text(priority)

    def normalize_urgency(self, urgency: Optional[str]) -> Optional[str]:
        """Normalize urgency into a stable string representation."""
        return self._normalize_text(urgency)

    def normalize_impact(self, impact: Optional[str]) -> Optional[str]:
        """Normalize impact into a stable string representation."""
        return self._normalize_text(impact)

    def normalize_category(self, category: Optional[str]) -> Optional[str]:
        """Normalize category into a stable string representation."""
        return self._normalize_text(category)

    def _normalize_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
