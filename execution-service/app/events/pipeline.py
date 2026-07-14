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
        logger.info("execution_plan_processed", extra={"plan_id": plan.plan_id, "investigation_id": plan.investigation_id})
