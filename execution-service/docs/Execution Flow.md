# Execution Flow

1. Consume `investigation.completed.v1`.
2. Build deterministic `ExecutionPlan` from snapshot and recommendations.
3. Evaluate all policies for each task.
4. Determine approval requirement and expiration.
5. Materialize queue with deterministic dependency ordering.
6. Publish lifecycle events.
7. Update task states through governed API operations.
8. Verify expected vs observed outcomes.
9. Persist immutable audit records.
