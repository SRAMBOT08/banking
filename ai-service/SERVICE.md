AI Service Contract

Responsibility:
- Interact with LLMs for explanations, executive summaries, missing evidence suggestions, and counterfactual reasoning. Must not perform business decisions or compute confidence.

Inputs:
- investigation.context.requests.v1

Outputs:
- ai.responses.v1

Kafka Topics Produced:
- ai.responses.v1

Kafka Topics Consumed:
- investigation.context.requests.v1

Database Ownership:
- None (stateless), may log requests for audit

External Integrations:
- LLM providers (Gemini) — credentials managed externally

Dependencies:
- shared library

Shared Models Used:
- shared.models.ai.*
