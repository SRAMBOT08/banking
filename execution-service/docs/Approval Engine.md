# Approval Engine

Approval behavior is deterministic and role-based:

- Automatic approval for low risk.
- Role-based pending approvals for SOC/Fraud/Compliance/Risk/Security.
- Expiration timestamps are deterministic from request time + configured minutes.
- Approval actions are audit logged.
