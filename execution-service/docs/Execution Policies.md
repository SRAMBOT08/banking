# Execution Policies

Implemented policy types:

- `RiskPolicy`
- `TenantPolicy`
- `SchedulingWindowPolicy`
- `ApprovalPolicy`
- `RetryPolicy`
- `RollbackPolicy`

Policy results map to:

- `ALLOWED`
- `DENIED`
- `APPROVAL_REQUIRED`
- `BLOCKED`
- `EXPIRED`
- `UNSUPPORTED`

All policy decisions include deterministic explanation + violations.
