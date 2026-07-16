from __future__ import annotations
from typing import Any
from .models import InvestigationContext, ValidationSummary


class ContextValidator:
    def validate_sources(self, results: dict[str, Any]) -> list[str]:
        return [source for source, result in results.items() if result is None]

    def validate(self, context: InvestigationContext) -> ValidationSummary:
        errors = []
        if not context.metadata.investigation_id:
            errors.append("investigation_id is required")
        if not context.metadata.correlation_id:
            errors.append("correlation_id is required")
        return ValidationSummary(valid=not errors, errors=errors, warnings=list(context.missing_information))
