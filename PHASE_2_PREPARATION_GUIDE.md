# Phase 2 Preparation Guide: Complete LangGraph Runtime

**Status**: Ready for Phase 2 Implementation  
**Prerequisite**: Phase 1 successfully deployed and tested  
**Timeline**: Estimated 4-6 hours implementation  

---

## Phase 2 Objective

Ensure every LangGraph node executes properly and updates investigation state with complete metadata tracking. The goal is to verify the 14-node workflow chain works end-to-end with proper state management.

---

## Current State (After Phase 1)

✅ CandidatePipeline invokes InvestigationOrchestrator  
✅ InvestigationState created with initial evidence/hypotheses  
✅ WorkflowEngine.start() called with compiled graph  
✅ Final state captured after workflow completes  
✅ Investigation updated and events published  

⚠️ **GAPS**: 
- LangGraph nodes may not properly receive/update InvestigationState
- Node execution tracking incomplete
- Progress metrics not calculated
- Retry metadata not fully recorded
- Duration tracking may have issues

---

## Phase 2 Implementation Checklist

### 1. Verify LangGraph Node Execution

**Task 1a: Check node handlers**
- Location: `investigation-service/app/agent/nodes/`
- For EACH node file, verify:
  ```python
  # Required structure:
  async def node_handler(state: InvestigationState) -> InvestigationState:
      execution = state.begin_node("node_name", metadata={...})
      try:
          # Perform node work
          state.evidence.append(...)  # Update state
          state.hypotheses.append(...)
          state.add_history({...})
          execution.finish(status="completed")
      except Exception as e:
          execution.finish(status="failed", error=str(e))
          raise
      return state
  ```
- Each node must call `state.begin_node()` and `state.finish_node()`

**Task 1b: Check GraphBuilder**
- Location: `investigation-service/app/agent/graph.py`
- Verify all 14 nodes are added to graph:
  1. collect_evidence
  2. retrieve_knowledge
  3. run_pattern_matching
  4. identify_missing_evidence (conditional loop)
  5. graph_analysis
  6. retrieve_history
  7. generate_hypotheses
  8. aggregate_confidence
  9. decision_engine (3-way conditional)
  10. checkpoint
  11. human_approval (self-loop)
  12. build_investigation
  13. generate_ai_report
  14. execution_planning
- Verify each node's input/output signature matches

**Task 1c: Check WorkflowEngine**
- Location: `investigation-service/app/agent/workflow.py`
- Verify `engine.start(state)` properly:
  - Invokes `graph.invoke({"...initial state..."}, config={"configurable": {"thread_id": investigation_id}})`
  - Returns final InvestigationState
  - Handles exceptions properly

### 2. Enhance Node State Updates

**Task 2a: Add progress calculation**
- Each node should calculate progress as (completed_nodes / total_nodes) * 100
- Store in state: `state.metadata["progress_percent"] = int(progress)`
- Update on every node transition

**Task 2b: Add execution metadata to each node**
```python
# After node completes:
state.execution_metadata = {
    "total_duration_ms": sum((exec.duration_ms or 0) for exec in state.node_executions),
    "current_node": state.current_node,
    "completed_nodes": len([e for e in state.node_executions if e.status == "completed"]),
    "failed_nodes": len([e for e in state.node_executions if e.status == "failed"]),
    "retry_count": state.retry_count,
    "failure_count": state.failure_count,
    "latest_error": state.node_executions[-1].error if state.node_executions and state.node_executions[-1].error else None,
}
```

**Task 2c: Add retry tracking**
- When node fails, node handler should call:
  ```python
  state.record_retry(f"Node {node_name} failed: {error}", node=node_name)
  # Then retry or escalate
  ```

### 3. Test Complete End-to-End Flow

**Task 3a: Set up test scenario**
```bash
# Terminal 1: Start Docker stack
docker compose up -d

# Wait for services to be healthy
docker compose ps

# Check investigation service logs
docker logs -f investigation-service | grep "workflow_execution"
```

**Task 3b: Run attack scenario**
```bash
# Terminal 2: Trigger a scenario
curl -X POST http://localhost:8080/api/v1/simulations/run \
  -H "Content-Type: application/json" \
  -d '{"scenario": "account_takeover", "tenant_id": "default"}'

# Or use the frontend UI
# Open http://localhost:3000
# Click "Run Account Takeover"
```

**Task 3c: Monitor workflow execution**
```bash
# Terminal 3: Watch logs in real-time
docker logs -f investigation-service | grep -E "workflow_execution|node_start|node_finish"

# Look for:
# ✅ workflow_execution_starting
# ✅ node_start: collect_evidence
# ✅ node_finish: collect_evidence (duration_ms: 245)
# ✅ node_start: retrieve_knowledge
# ... (all 14 nodes)
# ✅ workflow_execution_completed
# ✅ investigation_completed_published
```

**Task 3d: Verify event chain**
```bash
# Terminal 4: Check downstream services received completion event
docker logs case-service | grep "investigation.completed"
docker logs ai-report-service | grep "investigation.completed"
docker logs execution-service | grep "investigation.completed"
```

### 4. Add Node-Level Logging

**Task 4a: Create node execution logger**
- Location: Create `investigation-service/app/agent/node_logger.py`
- Content:
```python
from app.core.logger import get_logger
from app.agent.state import InvestigationState, NodeExecution

logger = get_logger("node_execution")

def log_node_start(state: InvestigationState, node_name: str):
    logger.info("node_start", extra={
        "investigation_id": state.investigation_id,
        "node": node_name,
        "status": "started",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

def log_node_finish(state: InvestigationState, execution: NodeExecution):
    logger.info("node_finish", extra={
        "investigation_id": state.investigation_id,
        "node": execution.node,
        "status": execution.status,
        "duration_ms": execution.duration_ms,
        "retry_count": execution.retry_count,
        "error": execution.error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

def log_workflow_progress(state: InvestigationState):
    completed = len([e for e in state.node_executions if e.status == "completed"])
    total = len(state.node_executions) + 1  # Include current node
    progress = int((completed / total) * 100) if total > 0 else 0
    logger.info("workflow_progress", extra={
        "investigation_id": state.investigation_id,
        "current_node": state.current_node,
        "completed_nodes": completed,
        "total_nodes": total,
        "progress_percent": progress,
        "current_confidence": state.final_confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
```

**Task 4b: Update each node to use logging**
- Import the logger functions
- Call at node start and finish
- Call progress logger after state updates

### 5. Handle Error Scenarios

**Task 5a: Retry logic**
- If a node fails:
  - Log failure with error message
  - Call state.record_retry()
  - Attempt retry (up to max_retries)
  - If retry fails, escalate or rollback

**Task 5b: Rollback logic**
- If workflow must rollback:
  - Find latest checkpoint in state.checkpoint_history
  - Revert to that checkpoint state
  - Set state.workflow_status = WorkflowStatus.ROLLED_BACK
  - Return to CandidatePipeline handler for event publishing

---

## Testing Strategy

### Unit Tests (Per Node)

For each node, create test like:

```python
# File: investigation-service/tests/test_node_handlers.py
import pytest
from app.agent.state import InvestigationState, WorkflowStatus
from app.agent.nodes.collect_evidence import collect_evidence_handler

@pytest.mark.asyncio
async def test_collect_evidence_updates_state():
    """Test that collect_evidence node updates InvestigationState."""
    initial_state = InvestigationState.new("inv-123", "tenant-1")
    initial_state.evidence = []
    
    result = await collect_evidence_handler(initial_state)
    
    assert result.investigation_id == "inv-123"
    assert len(result.node_executions) > 0
    assert result.node_executions[0].status == "completed"
    assert len(result.evidence) > 0
    assert result.current_node == "collect_evidence"
```

### Integration Tests (Full Workflow)

```python
# File: investigation-service/tests/test_full_workflow.py
@pytest.mark.asyncio
async def test_full_investigation_workflow():
    """Test complete 14-node workflow execution."""
    # Create investigation candidate
    candidate = CandidateInput(...)
    
    # Process through pipeline
    investigation = manager.process(candidate)
    agent_state = StateMapper.to_agent_state(investigation, "tenant-1")
    
    # Execute workflow
    orchestrator = InvestigationOrchestrator(tool_router, graph_builder)
    final_state = orchestrator.start(agent_state)
    
    # Verify execution
    assert final_state.workflow_status == WorkflowStatus.COMPLETED
    assert len(final_state.node_executions) == 14
    assert final_state.final_confidence > 0
    assert len(final_state.hypotheses) > 0
    assert final_state.execution_plan != {}
```

### End-to-End Tests (Docker)

```bash
#!/bin/bash
# File: tests/e2e_phase2.sh

set -e

echo "Phase 2: Testing Complete LangGraph Runtime"
echo "=============================================="

# 1. Start stack
echo "[1/5] Starting Docker stack..."
docker compose up -d
sleep 10

# 2. Verify services healthy
echo "[2/5] Verifying services..."
docker compose ps --services | while read service; do
    health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "N/A")
    echo "  $service: $health"
done

# 3. Publish test candidate
echo "[3/5] Publishing test candidate..."
./scripts/publish_candidate.sh account_takeover

# 4. Wait for workflow completion
echo "[4/5] Waiting for workflow completion..."
sleep 30

# 5. Verify execution
echo "[5/5] Verifying workflow execution..."
docker logs investigation-service | grep -E "workflow_execution_completed|node_finish" | wc -l
docker logs investigation-service | grep "investigation_completed_published"

echo ""
echo "✅ Phase 2 Testing Complete"
```

---

## Success Criteria for Phase 2

✅ All 14 LangGraph nodes execute in correct order  
✅ Each node receives InvestigationState as input  
✅ Each node updates InvestigationState with results  
✅ State.node_executions has 14 completed entries  
✅ Progress percentage increases from 0 to 100  
✅ Final confidence score calculated and stored  
✅ Execution metadata complete (durations, retry counts, etc.)  
✅ No exceptions in node handlers  
✅ Workflow completion event published to Kafka  
✅ Downstream services receive and process completion event  
✅ Investigation marked CLOSED in repository  
✅ Full end-to-end flow works without manual intervention  

---

## Troubleshooting Guide

### Problem: Nodes not executing
**Cause**: GraphBuilder not properly configured with nodes  
**Fix**: Check `investigation-service/app/agent/graph.py` - ensure all 14 nodes added to graph with correct names

### Problem: State not updating between nodes
**Cause**: Node handlers not calling `state.begin_node()` / `state.finish_node()`  
**Fix**: Add state update calls to every node handler

### Problem: Completion event not published
**Cause**: Workflow status not set to COMPLETED  
**Fix**: Check final node sets `state.workflow_status = WorkflowStatus.COMPLETED` before returning

### Problem: Memory errors on large investigations
**Cause**: InMemoryInvestigationRepository growing unbounded  
**Fix**: Implement cleanup/pagination in Phase 3

---

## Files to Examine/Modify in Phase 2

| Path | Purpose | Task |
|------|---------|------|
| `app/agent/nodes/*.py` | Node handlers | Verify state updates |
| `app/agent/graph.py` | LangGraph definition | Verify all 14 nodes |
| `app/agent/workflow.py` | Workflow engine | Verify invoke/return |
| `app/agent/state.py` | State model | Add progress fields |
| `tests/test_node_handlers.py` | Unit tests | Create node tests |
| `tests/test_full_workflow.py` | Integration tests | Create workflow tests |
| `scripts/publish_candidate.sh` | Test helper | Create if missing |

---

## Phase 2 → Phase 3 Transition

Once Phase 2 is complete and all tests pass:

1. **Take snapshot of working state** (git commit with message "Phase 2: Complete LangGraph Runtime")
2. **Document any deviations** from planned node structure
3. **Begin Phase 3**: Investigation Runtime State subsystem
   - Add runtime state exposure infrastructure
   - Track current node, stage, progress, confidence in real-time
   - Expose state via investigation service API

---

## Next: Phase 3 Overview (Sneak Peak)

Phase 3 will add the Runtime State subsystem that allows external services (Gateway, Frontend) to query:

```python
# Example Phase 3 endpoint
GET /api/v1/investigations/{id}/runtime

{
    "investigation_id": "inv-123",
    "current_stage": "HYPOTHESIS_GENERATION",
    "current_node": "generate_hypotheses",
    "progress_percent": 65,
    "nodes_completed": 9,
    "nodes_pending": 5,
    "current_confidence": 0.82,
    "hypotheses_count": 4,
    "evidence_count": 23,
    "execution_duration_ms": 12450,
    "status": "RUNNING",
    "last_updated": "2024-07-16T10:23:45.123Z"
}
```

This will feed real-time data to the frontend dashboard for visualization.

---

## Ready for Phase 2? ✅

All Phase 1 components are in place. The integration is ready for testing. Proceed with:

```bash
# 1. Deploy Phase 1 code to your environment
git commit -m "Phase 1: Investigation Agent Activation"
git push

# 2. Pull latest code
git pull

# 3. Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d

# 4. Monitor Phase 1 execution
docker logs -f investigation-service | grep -E "candidate_ingested|workflow_execution"

# 5. When Phase 1 verified, begin Phase 2 implementation
```

**Start Phase 2 when**: Phase 1 has executed end-to-end without errors and investigation.completed.v1 events are flowing to Kafka.
