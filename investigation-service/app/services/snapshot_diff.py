from __future__ import annotations

from typing import Dict

from app.models.snapshot import InvestigationSnapshot, SnapshotDiff


class SnapshotDiffEngine:
    @staticmethod
    def _by(items, key):
        return {key(item): item for item in items}

    def compare(self, before: InvestigationSnapshot, after: InvestigationSnapshot) -> SnapshotDiff:
        if before.metadata.investigation_id != after.metadata.investigation_id:
            raise ValueError("snapshots belong to different investigations")
        before_evidence = self._by(before.evidence, lambda item: item.evidence_id)
        after_evidence = self._by(after.evidence, lambda item: item.evidence_id)
        before_timeline = self._by(before.timeline, lambda item: item.event_id)
        after_timeline = self._by(after.timeline, lambda item: item.event_id)
        before_recs = self._by(before.recommendations, lambda item: item.recommendation_id)
        after_recs = self._by(after.recommendations, lambda item: item.recommendation_id)
        before_missing = self._by(before.missing_evidence, lambda item: item.evidence_type)
        after_missing = self._by(after.missing_evidence, lambda item: item.evidence_type)
        state_changes = {}
        priority_changes = {}
        if before.investigation.state != after.investigation.state:
            state_changes = {"from": before.investigation.state.value, "to": after.investigation.state.value}
        if before.investigation.priority != after.investigation.priority:
            priority_changes = {"from": before.investigation.priority.value, "to": after.investigation.priority.value}
        confidence_changes = {}
        if before.confidence != after.confidence:
            confidence_changes = {"from": before.confidence.score, "to": after.confidence.score}
        return SnapshotDiff(
            investigation_id=after.metadata.investigation_id,
            from_snapshot=before.metadata.snapshot_version,
            to_snapshot=after.metadata.snapshot_version,
            added_evidence=[after_evidence[key] for key in sorted(set(after_evidence) - set(before_evidence))],
            removed_evidence=[before_evidence[key] for key in sorted(set(before_evidence) - set(after_evidence))],
            confidence_changes=confidence_changes,
            timeline_added=[after_timeline[key] for key in sorted(set(after_timeline) - set(before_timeline))],
            timeline_removed=[before_timeline[key] for key in sorted(set(before_timeline) - set(after_timeline))],
            state_changes=state_changes,
            recommendation_added=[after_recs[key] for key in sorted(set(after_recs) - set(before_recs))],
            recommendation_removed=[before_recs[key] for key in sorted(set(before_recs) - set(after_recs))],
            priority_changes=priority_changes,
            missing_evidence_added=[after_missing[key] for key in sorted(set(after_missing) - set(before_missing))],
            missing_evidence_removed=[before_missing[key] for key in sorted(set(before_missing) - set(after_missing))],
        )
