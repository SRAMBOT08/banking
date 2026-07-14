# Execution Queue

Queue supports deterministic structures:

- FIFO ordering
- Priority ordering
- Dependency blocking
- Delayed/waiting buckets
- Retry queue
- Dead-letter queue

Readiness is recalculated from dependency completion set; no non-deterministic scheduling is used.
