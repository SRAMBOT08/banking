from __future__ import annotations
from typing import Any
from .models import CorrelationRecord, CorrelationSummary


class CorrelationEngine:
    """Find explicit deterministic references shared between source facts."""
    def correlate(self, sections: dict[str, list[dict[str, Any]]]) -> CorrelationSummary:
        records = []
        pairs = (("evidence", "threat"), ("threat", "knowledge"), ("knowledge", "graph"), ("graph", "history"), ("evidence", "history"))
        for left, right in pairs:
            for first in sections.get(left, []):
                first_keys = {str(first.get(key)) for key in ("id", "name", "entity_id", "account_id", "user_id") if first.get(key) is not None}
                for second in sections.get(right, []):
                    second_keys = {str(second.get(key)) for key in ("id", "name", "entity_id", "account_id", "user_id") if second.get(key) is not None}
                    shared = first_keys & second_keys
                    if shared:
                        records.append(CorrelationRecord(left_source=left, right_source=right, left_id=str(first.get("id", next(iter(shared)))), right_id=str(second.get("id", next(iter(shared)))), relation="shared_reference", explanation=f"shared reference: {sorted(shared)[0]}"))
        refs: dict[str, list[str]] = {}
        for record in records:
            key = f"{record.left_source}:{record.left_id}"
            refs.setdefault(key, []).append(f"{record.right_source}:{record.right_id}")
        return CorrelationSummary(records=records, cross_service_references=refs, related_intelligence=sorted(refs))
