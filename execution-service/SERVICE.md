Execution Service Contract

Responsibility:
- Ticketing, notifications, and workflow provider integrations (ServiceNow, Teams, Jira) via provider pattern.

Inputs:
- execution.requests.v1

Outputs:
- execution.status.v1

Kafka Topics Produced:
- execution.status.v1

Kafka Topics Consumed:
- execution.requests.v1

Database Ownership:
- None in Phase 1 (stateless providers); may persist audit logs in Phase 2

External Integrations:
- ServiceNow, Jira, Microsoft Teams (provider placeholders)

Dependencies:
- shared library

Shared Models Used:
- shared.models.execution.*
