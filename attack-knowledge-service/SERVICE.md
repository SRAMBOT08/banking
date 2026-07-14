Attack Knowledge Graph Service

Deterministic rule-based matcher that consumes evidence.graph.events.v1 and emits investigation.candidates.v1

Responsibilities:
- Load versioned attack patterns from patterns/ (YAML)
- Match incoming Evidence Graphs deterministically
- Score and explain candidate investigations
- Publish candidates to Kafka

No AI. No LLM. Deterministic only.
