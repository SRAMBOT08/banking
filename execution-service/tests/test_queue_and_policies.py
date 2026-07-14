from app.config.settings import Settings
from app.models import ExecutionCategory, ExecutionPlan, ExecutionTask
from app.policies.execution import CompositeExecutionPolicyEngine, RiskPolicy, SchedulingWindowPolicy, TenantPolicy
from app.queue.engine import DeterministicExecutionQueueEngine


def make_task(order: int, priority: int, deps=None):
    return ExecutionTask(
        correlation_id="c1",
        investigation_id="i1",
        tenant_id="t1",
        snapshot_version=1,
        recommendation_id=f"rec-{order}",
        task_title=f"task-{order}",
        task_description="desc",
        category=ExecutionCategory.SOC,
        priority=priority,
        deterministic_order=order,
        dependencies=deps or [],
        idempotency_key=f"k-{order}",
    )


def test_queue_dependency_blocking():
    tasks = [make_task(1, 90), make_task(2, 80, deps=["dep-x"])]
    queue = DeterministicExecutionQueueEngine().build_queue("p1", tasks)
    mapping = {t.task_id: t for t in tasks}
    queue = DeterministicExecutionQueueEngine().refresh_ready(queue, mapping)
    assert len(queue.pending_tasks) == 2


def test_policy_engine_returns_deterministic_set():
    settings = Settings(kafka_bootstrap="", execution_window_start_hour_utc=0, execution_window_end_hour_utc=23)
    engine = CompositeExecutionPolicyEngine([RiskPolicy(settings), TenantPolicy(), SchedulingWindowPolicy(settings)])
    task = make_task(1, 90)
    plan = ExecutionPlan(
        correlation_id="c1",
        investigation_id="i1",
        tenant_id="t1",
        snapshot_id="s1",
        snapshot_version=1,
        risk_score=50,
        confidence_score=80,
        tasks=[task],
    )
    decisions = engine.evaluate(plan, task)
    assert [d.policy_name for d in decisions] == ["risk_policy", "tenant_policy", "scheduling_policy"]
