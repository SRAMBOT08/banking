from __future__ import annotations

from typing import Any, Dict, List

from app.models import ExecutionCategory, ExecutionDependency, ExecutionPlan, ExecutionState, ExecutionTask, ExecutionTaskState


class ExecutionPlanner:
    """Transforms completed-investigation snapshots into deterministic execution plans."""

    def _category(self, recommendation: Dict[str, Any]) -> ExecutionCategory:
        scope = str(recommendation.get("scope") or recommendation.get("team") or "").casefold()
        if "fraud" in scope:
            return ExecutionCategory.FRAUD
        if "compliance" in scope:
            return ExecutionCategory.COMPLIANCE
        if "risk" in scope:
            return ExecutionCategory.RISK
        if "soc" in scope:
            return ExecutionCategory.SOC
        if "security" in scope:
            return ExecutionCategory.SECURITY
        return ExecutionCategory.OPERATIONS

    def build(self, payload: Dict[str, Any]) -> ExecutionPlan:
        metadata = payload.get("metadata", {})
        snapshot = payload.get("snapshot", payload)
        snapshot_meta = snapshot.get("metadata", metadata)
        investigation = snapshot.get("investigation", {})

        correlation_id = str(metadata.get("correlation_id") or payload.get("correlation_id") or snapshot_meta.get("snapshot_id") or investigation.get("investigation_id") or "execution-correlation")
        investigation_id = str(snapshot_meta.get("investigation_id") or investigation.get("investigation_id") or payload.get("investigation_id") or "unknown-investigation")
        tenant_id = str(metadata.get("tenant_id") or snapshot.get("metadata_context", {}).get("tenant_id") or payload.get("tenant_id") or "tenant-unknown")
        snapshot_id = str(snapshot_meta.get("snapshot_id") or "unknown-snapshot")
        snapshot_version = int(snapshot_meta.get("snapshot_version", 1))

        recommendations = payload.get("recommendations") or snapshot.get("recommendations", []) or payload.get("ai_recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = []

        risk_score = int(payload.get("risk_score") or payload.get("risk", {}).get("score") or 0)
        confidence_score = int(payload.get("confidence") or snapshot.get("confidence", {}).get("score") or 0)

        tasks: List[ExecutionTask] = []
        dependencies: List[ExecutionDependency] = []
        for index, recommendation in enumerate(sorted(recommendations, key=lambda item: str(item.get("recommendation_id") or item.get("id") or item.get("title") or ""))):
            recommendation_id = str(recommendation.get("recommendation_id") or recommendation.get("id") or f"REC-{index + 1}")
            priority = int(recommendation.get("priority", max(1, 100 - index)))
            dependency_ids = [str(value) for value in recommendation.get("depends_on", [])]
            task = ExecutionTask(
                correlation_id=correlation_id,
                investigation_id=investigation_id,
                tenant_id=tenant_id,
                snapshot_version=snapshot_version,
                recommendation_id=recommendation_id,
                task_title=str(recommendation.get("title") or recommendation.get("name") or f"Execution task {index + 1}"),
                task_description=str(recommendation.get("description") or recommendation.get("details") or "Deterministic execution task derived from recommendation"),
                category=self._category(recommendation),
                priority=priority,
                deterministic_order=index + 1,
                state=ExecutionTaskState.PLANNED,
                dependencies=dependency_ids,
                metadata={"source": "snapshot_recommendation", "recommendation": recommendation},
                idempotency_key=f"{investigation_id}:{snapshot_version}:{recommendation_id}",
            )
            tasks.append(task)
            for dep in dependency_ids:
                dependencies.append(ExecutionDependency(task_id=task.task_id, depends_on_task_id=dep))

        if not tasks:
            task = ExecutionTask(
                correlation_id=correlation_id,
                investigation_id=investigation_id,
                tenant_id=tenant_id,
                snapshot_version=snapshot_version,
                recommendation_id="REC-NONE",
                task_title="Manual deterministic review",
                task_description="No recommendation provided; create governed human review task.",
                category=ExecutionCategory.OPERATIONS,
                priority=1,
                deterministic_order=1,
                state=ExecutionTaskState.PLANNED,
                dependencies=[],
                metadata={"source": "fallback"},
                idempotency_key=f"{investigation_id}:{snapshot_version}:REC-NONE",
            )
            tasks = [task]

        return ExecutionPlan(
            correlation_id=correlation_id,
            investigation_id=investigation_id,
            tenant_id=tenant_id,
            snapshot_id=snapshot_id,
            snapshot_version=snapshot_version,
            risk_score=risk_score,
            confidence_score=confidence_score,
            policy_results=payload.get("policy_results", {}),
            context={
                "investigation_context": payload.get("investigation_context", snapshot.get("summary", {})),
                "graph_summary": payload.get("graph_summary", snapshot.get("graph", {})),
                "memory_summary": payload.get("investigation_memory_summary", {}),
                "ai_recommendations": payload.get("ai_recommendations", []),
            },
            plan_state=ExecutionState.CREATED,
            tasks=tasks,
            dependencies=dependencies,
        )
