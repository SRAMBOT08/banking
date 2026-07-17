# Agent Runtime Flow Specification

## Purpose
This document specifies the LangGraph-orchestrated investigation loop running in the Investigation Service. It details the 14-node graph structure, state management schemas, conditional routing, tool adapters, and NIM endpoint configurations.

## Overview
Lokii replaces single-prompt LLM agents with a structured, stateful Graph Workflow built using LangGraph. The runtime loop processes alerts through a 14-node sequence, querying tools (Evidence, Threat, Memory), determining confidence, and formatting CaseFiles. It supports checkpoints, rollback states, and operator overrides.

---

## Architecture

### Node Sequence Flow
The agent graph executes sequentially, utilizing conditional paths for loops and interruptions:

```
             START
               │
               ▼
       [collect_evidence] ◄────────────────────────────────┐
               │                                           │
               ▼                                           │
      [retrieve_knowledge]                                 │
               │                                           │
               ▼                                           │ (collect_more)
     [run_pattern_matching]                                │
               │                                           │
    [identify_missing_evidence] ──(evidence_route)─────────┤
               │                                           │
               ▼ (continue)                                │
        [graph_analysis]                                   │
               │                                           │
               ▼                                           │
       [retrieve_history]                                  │
               │                                           │
               ▼                                           │
      [generate_hypotheses]                                │
               │                                           │
               ▼                                           │
     [aggregate_confidence]                                │
               │                                           │
       [decision_engine] ──(decision_route)────────────────┘
               │
               ├───────────────────────┬───────────────────┐
               ▼ (approval)            ▼ (continue)        ▼ (more_evidence)
          [checkpoint]          [build_investigation]   [collect_evidence]
               │                       │
               ▼                       ▼
       [human_approval]        [generate_ai_report]
               │                       │
       (approval_route)                ▼
        ├── wait ──► [human_app] [execution_planning]
        └── resume ──► [build_inv]     │
                                       ▼
                                      END
```

---

## Detailed Explanation

### 1. Why LangGraph and Stateful Workflows?
Security investigations are non-linear processes. They require retrieving additional context, comparing findings with historical patterns, and executing human-in-the-loop approvals. LangGraph allows building stateful graphs with cycles, error recovery, and interruptions, preventing the fragility of stateless single-prompt agents.

### 2. Why Not a Single LLM?
Stateless LLM calls are non-deterministic, subject to hallucination, and struggle to coordinate multi-hop calculations. Segregating deterministic tasks (e.g. graph path traversals, confidence math) from text compilation ensures auditability and predictable execution.

### 3. InvestigationState Schema
Tracks investigation metrics across nodes. Detailed schema variables include:
- `investigation_id` (str): Unique investigation tracking identifier.
- `tenant_id` (str): Customer partition identifier.
- `workflow_status` (WorkflowStatus): State enum value (`NEW` to `COMPLETED`).
- `evidence` (List[dict]): List containing normalized telemetry facts.
- `hypotheses` (List[dict]): Generated incident scenarios and confidence scores.
- `selected_hypothesis` (dict): Target pattern selection.
- `final_confidence` (float): Deterministic assessment percentage.
- `node_executions` (List[NodeExecution]): Execution metrics (start, duration, retries, errors).
- `checkpoint_id` (str): Checkpoint registry identifier.

### 4. Node Action Directory
1. `collect_evidence`: Gathers telemetry from the Evidence Service.
2. `retrieve_knowledge`: Looks up corresponding patterns in the Knowledge Platform.
3. `run_pattern_matching`: Checks evidence subgraphs against ATT&CK templates.
4. `identify_missing_evidence`: Flags missing data variables needed to support a hypothesis.
5. `graph_analysis`: Traverses Neo4j linkages to identify target connections.
6. `retrieve_history`: Searches the Memory Service for past incident similarity.
7. `generate_hypotheses`: Formulates potential threat scenarios.
8. `aggregate_confidence`: Calculates the final confidence score.
9. `decision_engine`: Determines if the case requires escalation or containment.
10. `checkpoint`: Captures state before human validation.
11. `human_approval`: Suspends runtime loop using LangGraph `interrupt()` until approved.
12. `build_investigation`: Combines metadata into CaseFiles.
13. `generate_ai_report`: Invokes LLM providers to compile SOC and compliance summaries.
14. `execution_planning`: Assembles mitigation action tasks.

---

## Workflow

### Stateful Execution Cycle
1. **Initiate**: Candidate telemetry triggers `StateMapper.to_agent_state()`, mapping data to the `InvestigationState` model.
2. **Execute**: The compiled graph starts executing sequential nodes.
3. **Branch**: If `identify_missing_evidence` flags gaps, the flow routes back to `collect_evidence`.
4. **Approve**: If the risk score warrants verification, the graph writes a checkpoint and interrupts.
5. **Resume**: Operator writes the override variable, and the graph resumes from the checkpoint.
6. **Conclude**: Saves the final state to PostgreSQL and publishes to `investigation.completed.v1`.

---

## Design Decisions
- **Isolation of LLM calls**: AI operations are restricted to `generate_ai_report` and explanations, while decisions and confidence scoring remain deterministic.
- **In-Memory Checkpointing (MemorySaver)**: Used in the MVP for simplicity; designed for future migration to PostgreSQL checkpointers.

## Best Practices
- **Explicit Transitions**: Graph transitions must be validated against `ALLOWED_TRANSITIONS` inside `InvestigationState`.
- **Defensive State Mapping**: Copy state variables defensively during transitions to prevent concurrent write corruption.

## Future Enhancements
- Replace the LangGraph `MemorySaver` checkpointer with a PostgreSQL-backed checkpointer.
- Add support for parallel node execution to reduce end-to-end processing latency.
