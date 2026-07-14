from app.config.settings import Settings
from app.models import ExecutionTaskState
from app.repositories.inmemory import ExecutionRepository
from app.services.platform import ExecutionPlatformService


def sample_payload():
    return {
        "metadata": {"correlation_id": "corr-1", "tenant_id": "tenant-1"},
        "snapshot": {
            "metadata": {"snapshot_id": "snap-1", "snapshot_version": 7, "investigation_id": "inv-1"},
            "investigation": {"investigation_id": "inv-1"},
            "confidence": {"score": 83},
            "recommendations": [
                {"recommendation_id": "rec-2", "title": "SOC review", "scope": "soc", "priority": 90},
                {"recommendation_id": "rec-1", "title": "Fraud review", "scope": "fraud", "priority": 95, "depends_on": ["manual-dep"]},
            ],
        },
        "risk_score": 65,
        "policy_results": {"bank": "ok"},
    }


def test_create_plan_policy_and_queue_deterministic_order():
    service = ExecutionPlatformService(Settings(kafka_bootstrap=""), ExecutionRepository())
    plan, policy, approvals = service.create_plan(sample_payload())
    assert plan.snapshot_version == 7
    assert [task.recommendation_id for task in plan.tasks] == ["rec-1", "rec-2"]
    assert all(task.state in {ExecutionTaskState.WAITING_APPROVAL, ExecutionTaskState.READY, ExecutionTaskState.FAILED} for task in plan.tasks)
    assert len(policy) == 6
    assert len(approvals) >= 1


def test_approve_retry_cancel_and_patch():
    service = ExecutionPlatformService(Settings(kafka_bootstrap=""), ExecutionRepository())
    plan, _, _ = service.create_plan(sample_payload())
    task = plan.tasks[0]
    approved = service.approve_task(task.task_id, "SOC_APPROVER", "approved")
    assert approved.state == ExecutionTaskState.APPROVED

    retried = service.retry_task(task.task_id, "retry")
    assert retried.retry_count == 1

    patched, verification = service.patch_task(task.task_id, state="COMPLETED", expected_result={"status": "ok"}, observed_result={"status": "ok"})
    assert patched.state == ExecutionTaskState.COMPLETED
    assert verification is not None

    cancelled = service.cancel_task(task.task_id, "cancel")
    assert cancelled.state == ExecutionTaskState.CANCELLED


def test_replay_and_statistics():
    service = ExecutionPlatformService(Settings(kafka_bootstrap=""), ExecutionRepository())
    plan, _, _ = service.create_plan(sample_payload())
    service.replay_plan(plan.plan_id)
    stats = service.statistics()
    assert stats.plan_count == 1
    assert stats.task_count == 2
    assert "COMPLETED" in stats.by_state or "WAITING_APPROVAL" in stats.by_state
