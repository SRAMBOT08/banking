from __future__ import annotations

from app.core.logger import get_logger

logger = get_logger("execution_pipeline")


class ExecutionPipeline:
    def __init__(self, platform, publisher):
        self.platform = platform
        self.publisher = publisher

    async def handle_completed_investigation(self, event: dict):
        plan, decisions, approvals = self.platform.create_plan(event)
        self.publisher.publish_plan_created(plan.model_dump(mode="json"), plan.plan_id)
        for decision in decisions:
            self.publisher.publish_policy_checked(decision.model_dump(mode="json"), plan.plan_id)
        for approval in approvals:
            self.publisher.publish_awaiting_approval(approval.model_dump(mode="json"), plan.plan_id)
        if not approvals:
            self.publisher.publish_ready(plan.model_dump(mode="json"), plan.plan_id)
            self.publisher.publish_execution_completed(plan, event)
        logger.info("execution_plan_processed", extra={"plan_id": plan.plan_id, "investigation_id": plan.investigation_id})

    async def handle_report_generated(self, event: dict):
        report = event.get("report", {})
        case_file = report.get("case_file", {}) or event.get("case_file", {})
        metadata = case_file.get("metadata", {})
        recommendations = case_file.get("recommendations", {})
        payload = {
            **event,
            "metadata": metadata,
            "investigation_id": event.get("investigation_id") or metadata.get("investigation_id"),
            "tenant_id": event.get("tenant_id") or metadata.get("tenant_id"),
            "correlation_id": event.get("correlation_id") or metadata.get("correlation_id"),
            "recommendations": recommendations.get("recommendations", []) if isinstance(recommendations, dict) else recommendations,
        }
        await self.handle_completed_investigation(payload)
