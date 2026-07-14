# Execution State Machine

Task states:

- `CREATED`
- `PLANNED`
- `WAITING_POLICY`
- `POLICY_APPROVED`
- `WAITING_APPROVAL`
- `APPROVED`
- `READY`
- `QUEUED`
- `RUNNING`
- `VERIFYING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`
- `ROLLED_BACK`

Only deterministic transitions are allowed by orchestrator operations. No random or probabilistic branching is used.
