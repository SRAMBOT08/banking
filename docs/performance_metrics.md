# Integration Performance Metrics

Metrics are measured by the deterministic harness at runtime, not fabricated. Each `StageMetric` records start time, completion time, record count, retries, failures, and correlation identifiers.

Run `python -m integration.run` to print per-scenario aggregate latency. The harness is intentionally in-process, so these values measure transformation and contract overhead only; they are not representative of networked Kafka, database, or ServiceNow latency.

Tracked identifiers:

- Correlation ID
- Investigation ID
- Case ID
- Execution ID
- Report ID
- Kafka message ID

Tracked timings:

- Stage latency
- Queue/transport boundary placeholder
- Processing latency
- Retry count
- Failure count
