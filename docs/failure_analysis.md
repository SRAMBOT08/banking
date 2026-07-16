# Integration Failure Analysis

| Failure | Detection | Current handling | Production follow-up |
|---|---|---|---|
| Missing event identity | contract validator | fail fast | dead-letter malformed messages |
| Duplicate event | ingestion dedupe contract | skip duplicate | durable Redis/Kafka idempotency key |
| Kafka unavailable | transport boundary | retry/DLQ required | configure retry policy and DLQ topic |
| Candidate schema mismatch | contract report | reject incompatible payload | canonical candidate v1 adapter |
| Missing intelligence source | aggregation contract | preserve empty source with provenance | service readiness and timeout policy |
| Case/report failure | downstream API contract | retain CaseFile and retry request | durable orchestration/outbox |
| Policy denied | execution policy | no adapter call | audit policy decision |
| ServiceNow unavailable | adapter result | retry and failure audit | circuit breaker and DLQ |
| Approval expiry | approval record | execution blocked | scheduled expiry worker |

The harness fails fast on identity and required artifact violations and uses a mock ServiceNow result so credentials are not required for deterministic CI.
