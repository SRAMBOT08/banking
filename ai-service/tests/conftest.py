import pytest


@pytest.fixture
def snapshot_payload():
    return {
        "metadata": {"snapshot_id": "snap-1", "snapshot_version": 1, "investigation_id": "inv-1", "created_at": "2026-07-14T00:00:00Z"},
        "investigation": {"investigation_id": "inv-1", "priority": "HIGH", "state": "READY_FOR_AI"},
        "timeline": [{"event_id": "time-1", "event_type": "candidate", "timestamp": "2026-07-14T00:00:00Z"}],
        "evidence": [{"evidence_id": "ev-1", "evidence_type": "login", "confidence": 90}],
        "hypotheses": [{"hypothesis_id": "hyp-1", "pattern_name": "account_takeover", "confidence": 80}],
        "confidence": {"score": 80, "pattern_score": 80},
        "confidence_history": [{"timestamp": "2026-07-14T00:00:00Z", "score": 80, "reason": "candidate"}],
        "recommendations": [{"recommendation_id": "rec-1", "title": "Collect device evidence"}],
        "missing_evidence": [{"evidence_type": "device", "reason": "required"}],
        "related_entities": ["user:user-1"],
        "related_investigations": [],
        "graph": {"nodes": [{"id": "inv-1", "type": "investigation"}], "edges": []},
        "metadata_context": {"tenant_id": "tenant-1"},
        "summary": {"snapshot_id": "snap-1", "snapshot_version": 1, "investigation_id": "inv-1", "priority": "HIGH", "confidence": 80},
    }
