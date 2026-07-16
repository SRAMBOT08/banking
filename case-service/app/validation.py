from __future__ import annotations
from typing import Any
from .exceptions import ContextValidationError


class ContextValidator:
    REQUIRED = ('metadata',)
    def validate(self, context: Any) -> None:
        data = context.model_dump(mode='python') if hasattr(context, 'model_dump') else context
        if not isinstance(data, dict): raise ContextValidationError('InvestigationContext must be a mapping or Pydantic model')
        metadata = data.get('metadata') or {}
        investigation_id = metadata.get('investigation_id')
        tenant_id = metadata.get('tenant_id')
        if not investigation_id: raise ContextValidationError('metadata.investigation_id is required')
        if not tenant_id: raise ContextValidationError('metadata.tenant_id is required')
        if not metadata.get('correlation_id'): raise ContextValidationError('metadata.correlation_id is required')
