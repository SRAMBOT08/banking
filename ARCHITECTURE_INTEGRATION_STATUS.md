# Lokii Platform: Architecture Integration Status & Timeline

**Current Phase**: 1 (COMPLETE) / 15  
**Overall Progress**: 7% Complete | 93% Remaining  
**Last Updated**: 2026-07-16  

---

## Integration Timeline Overview

```
Phase 1: Agent Activation ..................... [✅ COMPLETE]
Phase 2: LangGraph Runtime .................... [ ] IN QUEUE
Phase 3: Runtime State Subsystem ............. [ ] IN QUEUE
Phase 4: Runtime State API ................... [ ] IN QUEUE
Phase 5: Investigation Timeline API ......... [ ] IN QUEUE
Phase 6: Graph Runtime API ................... [ ] IN QUEUE
Phase 7: Frontend Integration ................ [ ] IN QUEUE
Phase 8: Attack Simulator Integration ....... [ ] IN QUEUE
Phase 9: Real-Time Synchronization .......... [ ] IN QUEUE
Phase 10: Dashboard Replacement .............. [ ] IN QUEUE
Phase 11: Investigation Workspace ............ [ ] IN QUEUE
Phase 12: Progress Visualization ............. [ ] IN QUEUE
Phase 13: Pipeline Visualization ............. [ ] IN QUEUE
Phase 14: Health Synchronization ............. [ ] IN QUEUE
Phase 15: End-to-End Validation .............. [ ] IN QUEUE
```

---

## Phase 1: Investigation Agent Activation ✅ COMPLETE

**Status**: Code complete, ready for testing  
**Duration**: Complete  
**Files Changed**: 4 | **Lines Added**: ~180  

### What Phase 1 Did

Wired the Kafka candidate pipeline directly into the LangGraph Investigation Agent, making the agent the sole execution path for candidate processing.

### Implementation Summary

```
Before Phase 1:
  Kafka → CandidatePipeline → InvestigationManager → No LangGraph → Events published

After Phase 1:
  Kafka → CandidatePipeline → InvestigationManager → StateMapper → 
  InvestigationOrchestrator → WorkflowEngine → GraphBuilder → 
  14-Node LangGraph Workflow → Final State → Investigation Updated → 
  All Events Published (including investigation.completed.v1)
```

### Components Activated

- ✅ ToolRouter (Evidence, Knowledge, Threat, Graph, Memory tools)
- ✅ CheckpointManager (in-memory, Phase 2 adds persistence)
- ✅ ReasoningEngine (injected into orchestrator)
- ✅ DecisionEngine (injected into orchestrator)
- ✅ InvestigationPlanner + GraphBuilder
- ✅ WorkflowEngine with proper invoke/return
- ✅ StateMapper for bidirectional conversion
- ✅ investigation.completed.v1 event publishing

### Critical Files Modified

| File | Change Type | Impact |
|------|-------------|--------|
| `app/pipeline/candidate_consumer.py` | REWRITE | Entry point for agent execution |
| `app/agent/state_mapper.py` | NEW | Bidirectional state conversion |
| `app/agent/investigation_orchestrator.py` | ENHANCE | Component injection pattern |
| `app/main.py` | UPDATE | Dependency passing |

### Test Requirements (For Phase 1 Validation)

```bash
# Prerequisites: Docker stack running, Kafka operational
docker compose up -d

# Run test candidate scenario
curl -X POST http://localhost:8080/api/v1/simulations/run \
  -H "Content-Type: application/json" \
  -d '{"scenario": "account_takeover"}'

# Verify execution logs
docker logs investigation-service | grep -E "candidate_ingested|workflow_execution_completed|investigation_completed_published"

# Expected: All 3 log lines present without errors
```

---

## Phase 2: Complete LangGraph Runtime ⏳ QUEUED

**Est. Duration**: 4-6 hours  
**Blocker**: Phase 1 must be verified  
**Focus**: Node execution, state updates, metadata tracking  

### What Phase 2 Will Do

Ensure all 14 LangGraph nodes execute properly, update InvestigationState with complete metadata, and handle error/retry scenarios.

### Tasks

1. **Verify Node Execution** (1h)
   - Inspect all 14 node handlers
   - Verify they receive and return InvestigationState
   - Check begin_node() and finish_node() calls

2. **Add Progress Tracking** (1h)
   - Calculate progress as percentage complete
   - Update state.metadata["progress_percent"]
   - Log progress after each node

3. **Add Execution Metadata** (1h)
   - Track node duration_ms
   - Record retry_count per node
   - Store latest error messages
   - Calculate total execution duration

4. **Add Node-Level Logging** (1h)
   - Create node_logger.py
   - Log node_start, node_finish, workflow_progress
   - Enable real-time monitoring

5. **Implement Error Handling** (1h)
   - Retry logic (configurable max_retries)
   - Rollback logic (revert to checkpoint)
   - Proper error propagation

6. **Test End-to-End** (2h)
   - Unit tests per node
   - Integration test for full workflow
   - Docker end-to-end test script
   - Verify all events published

### Success Metrics

- All 14 nodes execute in order
- state.node_executions has 14 entries
- progress_percent goes from 0→100
- execution_metadata complete
- investigation.completed.v1 published
- No exceptions in flow

---

## Phase 3: Investigation Runtime State ⏳ QUEUED

**Est. Duration**: 3-4 hours  
**Blocker**: Phase 2 complete  
**Focus**: Runtime state exposure infrastructure  

### What Phase 3 Will Do

Add a runtime state subsystem that tracks and exposes:
- Current node executing
- Current stage (COLLECTING_EVIDENCE, HYPOTHESIS_GENERATION, etc.)
- Completed/pending/failed nodes
- Progress percentage
- Current confidence level
- Execution duration
- Retry counts
- Checkpoint metadata

### Tasks

1. **Enhance InvestigationState** (1h)
   - Add runtime_stage field
   - Add completed_nodes list
   - Add pending_nodes list
   - Add failed_nodes list
   - Calculation methods for progress

2. **Create RuntimeStateService** (1h)
   - Location: `investigation-service/app/services/runtime_state.py`
   - Query current state by investigation_id
   - Calculate progress metrics
   - Track stage transitions

3. **Add State Persistence** (1h)
   - Store runtime state in cache/DB
   - Enable state recovery
   - Support concurrent investigations

4. **Create Repository** (1h)
   - Location: `investigation-service/app/repositories/runtime_state_repository.py`
   - get(), save(), list() methods
   - Support for in-memory and persistent backends

### Deliverables

- RuntimeStateService with query API
- InvestigationRuntimeState model
- Repository pattern implementation
- No frontend changes yet (only backend services)

---

## Phase 4: Runtime State API ⏳ QUEUED

**Est. Duration**: 2 hours  
**Blocker**: Phase 3 complete  
**Focus**: Gateway integration for runtime state  

### What Phase 4 Will Do

Expose runtime state through Gateway API so frontend can query live investigation progress.

### New Gateway Route

```
GET /api/v1/investigations/{id}/runtime
↓
Investigation Service: GET /investigations/{id}/runtime
↓
Returns:
{
    "investigation_id": "inv-123",
    "current_stage": "HYPOTHESIS_GENERATION",
    "current_node": "generate_hypotheses",
    "progress_percent": 65,
    "nodes_completed": 9,
    "nodes_pending": 5,
    "nodes_failed": 0,
    "current_confidence": 0.82,
    "hypotheses_count": 4,
    "evidence_count": 23,
    "execution_duration_ms": 12450,
    "status": "RUNNING",
    "retry_count": 0,
    "last_updated": "2024-07-16T10:23:45.123Z",
    "checkpoint_id": "cp-abc123"
}
```

### Tasks

1. **Add Investigation Service Route** (30m)
   - `GET /investigations/{id}/runtime`
   - Calls RuntimeStateService.get()
   - Returns InvestigationRuntimeState

2. **Add Gateway Proxy** (30m)
   - `GET /api/v1/investigations/{id}/runtime`
   - Proxies to investigation service
   - Adds auth/validation middleware

3. **Add Response DTO** (30m)
   - Location: `gateway/app/schemas/investigation_runtime.py`
   - Type-safe response envelope
   - Consistent with other Gateway responses

4. **Test Integration** (30m)
   - Query running investigation
   - Verify response structure
   - Verify data accuracy

---

## Phase 5: Investigation Timeline API ⏳ QUEUED

**Est. Duration**: 3 hours  
**Blocker**: Phase 2 complete (to generate timeline events)  
**Focus**: Live timeline event exposition  

### What Phase 5 Will Do

Create API endpoint that returns actual investigation timeline events emitted during workflow execution.

### New Gateway Route

```
GET /api/v1/investigations/{id}/timeline
↓
Returns:
[
  {
    "timestamp": "2024-07-16T10:23:00Z",
    "event_type": "NODE_START",
    "node": "collect_evidence",
    "message": "Collecting evidence from all sources"
  },
  {
    "timestamp": "2024-07-16T10:23:10Z",
    "event_type": "EVIDENCE_FOUND",
    "count": 23,
    "message": "Found 23 evidence items"
  },
  {
    "timestamp": "2024-07-16T10:23:15Z",
    "event_type": "NODE_COMPLETE",
    "node": "collect_evidence",
    "duration_ms": 15234
  },
  ... (all events in chronological order)
]
```

### Tasks

1. **Add Timeline Event Capture** (1h)
   - Every state.add_history() call captures event
   - Include timestamps, event types, metadata
   - Persist to timeline store

2. **Create TimelineRepository** (1h)
   - Query timeline by investigation_id
   - Filter by event type
   - Pagination support

3. **Add Service Route** (30m)
   - Investigation service GET /investigations/{id}/timeline
   - Gateway proxy GET /api/v1/investigations/{id}/timeline

4. **Test Integration** (30m)
   - Run scenario
   - Query timeline
   - Verify events in order

---

## Phase 6: Graph Runtime API ⏳ QUEUED

**Est. Duration**: 3 hours  
**Blocker**: Phase 2 complete (to populate graph)  
**Focus**: Live relationship graph exposition  

### What Phase 6 Will Do

Expose the investigation's entity relationship graph in real-time as it evolves.

### New Gateway Route

```
GET /api/v1/investigations/{id}/graph
↓
Returns:
{
  "nodes": [
    {"id": "user-123", "type": "user", "properties": {...}},
    {"id": "ip-456", "type": "ip_address", "properties": {...}},
    ...
  ],
  "edges": [
    {"source": "user-123", "target": "ip-456", "type": "logged_in_from", "confidence": 0.95},
    ...
  ],
  "stats": {
    "total_nodes": 42,
    "total_edges": 156,
    "avg_confidence": 0.87,
    "node_types": {"user": 10, "ip": 15, "domain": 12, ...}
  }
}
```

### Tasks

1. **Enhance Graph Building** (1h)
   - Store nodes and edges in InvestigationState
   - Update as evidence analyzed
   - Calculate confidence per relationship

2. **Create GraphRepository** (1h)
   - Query graph by investigation_id
   - Support filtering by node/edge type
   - Export to JSON format

3. **Add Service Route** (30m)
   - Investigation service GET /investigations/{id}/graph
   - Gateway proxy GET /api/v1/investigations/{id}/graph

4. **Test Integration** (30m)
   - Run scenario
   - Query graph at different points
   - Verify graph evolution

---

## Phase 7: Frontend Integration ⏳ QUEUED

**Est. Duration**: 8-10 hours  
**Blocker**: Phases 4, 5, 6 complete  
**Focus**: Replace all mock data with live APIs  

### What Phase 7 Will Do

Remove all hardcoded mock data from frontend and replace with live TanStack React Query hooks that call backend APIs.

### Files to Modify

1. **Delete** `frontend/src/lib/mock.ts` (entire file)
   - Remove all fixture data definitions
   - Remove exports

2. **Update** `frontend/src/components/lokii-app.tsx`
   - Remove all mock data imports
   - Add useQuery hooks for each data type
   - Bind all views to API responses

3. **Add Query Hooks** (new file)
   - Location: `frontend/src/hooks/useInvestigations.ts`
   - Hook: `useInvestigations(tenantId)` - list all investigations
   - Hook: `useInvestigation(id)` - single investigation details
   - Hook: `useInvestigationTimeline(id)` - timeline events
   - Hook: `useInvestigationGraph(id)` - relationship graph
   - Hook: `useInvestigationRuntime(id)` - current execution state
   - Polling intervals: 5s for timeline, 2s for runtime, 5s for investigation

4. **Update Dashboard** (30m)
   - Replace hardcoded KPIs with API data
   - Load active investigations count
   - Load threat level from aggregated data
   - Load recent cases from API

5. **Update Investigation Page** (2h)
   - Timeline: use useInvestigationTimeline
   - Graph: use useInvestigationGraph
   - Details: use useInvestigation
   - Runtime: use useInvestigationRuntime with auto-refresh

6. **Update System Health** (1h)
   - Use /api/v1/platform/health
   - Display actual service states
   - Auto-refresh every 15s

7. **Test All Views** (2h)
   - Run scenario
   - Open frontend
   - Verify all data loads from APIs
   - No mock data rendered
   - Auto-refresh works

### Mock Data Removal

Files/locations with mock data to remove:
- ✅ `frontend/src/lib/mock.ts` - DELETE
- ✅ All imports of mock in components - REMOVE
- ✅ All hardcoded arrays in state - REPLACE with useQuery

### Success Metrics

- Mock.ts file deleted
- No mock data references remain
- All views use live APIs
- Data updates in real-time
- No errors in browser console

---

## Phase 8: Attack Simulator Integration ⏳ QUEUED

**Est. Duration**: 2 hours  
**Blocker**: Phase 7 complete (for UI testing)  
**Focus**: Wire simulator run button to investigation tracking  

### What Phase 8 Will Do

Enable the "Run Scenario" button to properly start a simulation and automatically track the resulting investigation.

### UI Changes

```
Before: Run button → no visible effect
After:  Run button → simulation starts → 
        correlation_id assigned → 
        investigation created → 
        frontend automatically loads investigation and watches execution
```

### Task List

1. **Enhance Simulator Service** (30m)
   - POST /api/v1/simulations/run endpoint
   - Returns: { simulation_id, investigation_id, correlation_id }
   - Publishes initial events to Kafka

2. **Add Frontend Handler** (1h)
   - `frontend/src/hooks/useRunScenario.ts`
   - useMutation hook for scenario execution
   - Automatically navigates to investigation view
   - Starts polling investigation runtime

3. **Add Polling Setup** (30m)
   - Automatically poll investigation.runtime every 2s
   - Automatically poll investigation.timeline every 3s
   - Update UI as data arrives

### Success Metrics

- Run Scenario button works
- Investigation automatically appears
- UI updates as workflow executes
- No manual page refresh needed

---

## Phase 9: Real-Time Synchronization ⏳ QUEUED

**Est. Duration**: 3 hours  
**Blocker**: Phases 4-6 complete  
**Focus**: Implement TanStack Query polling infrastructure  

### What Phase 9 Will Do

Configure proper polling intervals for all dashboard data sources so UI stays in sync without WebSockets.

### Polling Intervals

```
GET /api/v1/investigations/{id}/runtime
  Interval: 2 seconds
  Used by: Progress bar, current node display

GET /api/v1/investigations/{id}/timeline
  Interval: 3 seconds
  Used by: Timeline event list

GET /api/v1/investigations/{id}
  Interval: 5 seconds
  Used by: Investigation details

GET /api/v1/investigations/{id}/graph
  Interval: 5 seconds
  Used by: Relationship graph

GET /api/v1/cases
  Interval: 5 seconds
  Used by: Cases list

GET /api/v1/reports
  Interval: 5 seconds
  Used by: Reports list

GET /api/v1/platform/health
  Interval: 15 seconds
  Used by: System health dashboard
```

### Tasks

1. **Configure Query Cache** (1h)
   - Set staleTime for each query type
   - Set refetchInterval based on polling schedule
   - Handle errors gracefully

2. **Add Loading States** (1h)
   - Show loading spinners during fetch
   - Display "last updated" timestamp
   - Handle offline scenarios

3. **Test Polling** (1h)
   - Run scenario
   - Monitor network tab (should see requests at right intervals)
   - Verify UI updates
   - Check for polling storms

### Success Metrics

- Network requests follow polling schedule
- No missed updates
- No unnecessary requests
- Graceful error handling

---

## Phase 10: Dashboard Replacement ⏳ QUEUED

**Est. Duration**: 4 hours  
**Blocker**: Phases 4-9 complete  
**Focus**: Make dashboard dynamic with live data  

### What Phase 10 Will Do

Replace all hardcoded dashboard values with real-time API data.

### Dashboard Sections to Update

1. **Key Performance Indicators** (KPIs)
   - Active Investigations: COUNT FROM GET /api/v1/investigations
   - Threat Level: AGGREGATED FROM recent investigations
   - MITRE Coverage: CALCULATED FROM threat intelligence
   - Running Simulations: COUNT FROM simulations endpoint
   - Execution Queue: COUNT FROM execution service
   - Recent Reports: LAST 5 FROM /api/v1/reports
   - Platform Health: FROM /api/v1/platform/health
   - Recent Cases: LAST 5 FROM /api/v1/cases

2. **Dashboard Charts** (if applicable)
   - Investigation status breakdown
   - Threat level distribution
   - Case resolution timeline
   - Execution success rate

3. **Recent Items Lists**
   - Latest 5 investigations
   - Latest 5 cases
   - Latest 5 reports
   - Latest 5 executions

### Tasks

1. **Create Dashboard Service** (1h)
   - Queries all required endpoints
   - Aggregates data
   - Calculates metrics

2. **Update Dashboard Component** (2h)
   - Remove mock data
   - Add useQuery hooks
   - Bind to live data
   - Handle loading states

3. **Add Visualization** (1h)
   - Charts/graphs for trends
   - Status indicators
   - Color coding (red/yellow/green)

### Success Metrics

- No hardcoded values visible
- All numbers from API
- Updates every 5-15 seconds
- No errors when no data

---

## Phase 11: Investigation Workspace ⏳ QUEUED

**Est. Duration**: 5 hours  
**Blocker**: Phases 4-9 complete  
**Focus**: Make all workspace tabs live  

### What Phase 11 Will Do

Ensure every tab in the Investigation Workspace uses live backend data exclusively.

### Tabs to Update

| Tab | API | Status |
|-----|-----|--------|
| Timeline | GET /investigations/{id}/timeline | Phase 5 |
| Evidence | GET /investigations/{id}/evidence | New |
| Relationships | GET /investigations/{id}/graph | Phase 6 |
| Intelligence | GET /investigations/{id}/intelligence | New |
| Threat Data | GET /threat-intelligence/{id} | Service needs route |
| Knowledge Platform | GET /knowledge/{id} | Service needs route |
| AI Reports | GET /reports?investigation_id={id} | Phase 10 |
| Execution | GET /executions?investigation_id={id} | Service needs route |
| Audit | GET /cases?investigation_id={id} | Service needs route |

### New APIs Needed

1. Evidence API: GET /api/v1/investigations/{id}/evidence
2. Intelligence API: GET /api/v1/investigations/{id}/intelligence
3. Threat API: GET /api/v1/threat-intelligence/query
4. Knowledge API: GET /api/v1/knowledge/query
5. Execution API: GET /api/v1/executions?investigation_id={id}
6. Audit API: GET /api/v1/cases?investigation_id={id}

### Tasks

1. **Add Missing Backend Routes** (2h)
   - Each service adds new route
   - Gateway adds proxy route
   - Return proper DTO

2. **Add Query Hooks** (1h)
   - Create hooks for each tab
   - Implement filtering/pagination

3. **Update Tab Components** (2h)
   - Remove any remaining mock data
   - Bind to useQuery hooks
   - Add loading states

### Success Metrics

- All tabs show live data
- No mock data visible
- Tabs update automatically
- Smooth user experience

---

## Phase 12: Progress Visualization ⏳ QUEUED

**Est. Duration**: 2 hours  
**Blocker**: Phase 4 complete (runtime API)  
**Focus**: Show investigation agent executing in real-time  

### What Phase 12 Will Do

Visualize the Investigation Agent's progress as it executes each node.

### UI Component

```
Investigation Progress
════════════════════════════════════════════════════════

🔄 Collecting Evidence
████████████████░░░░░░░░░░░░  30%

Next: Retrieve Knowledge
```

### Animated Display

```
📊 Evidence Collection
████████████████░░░░░░░░░░░░  40%  [2.5s elapsed]

        ↓ (auto-advance every 2s)

📚 Knowledge Retrieval
██████░░░░░░░░░░░░░░░░░░░░░░  15%  [0.8s elapsed]

        ↓ (auto-advance every 2s)

🔍 Pattern Matching
████████████░░░░░░░░░░░░░░░░░  50%  [5.2s elapsed]
```

### Tasks

1. **Create Progress Component** (1h)
   - Location: `frontend/src/components/InvestigationProgress.tsx`
   - Shows current stage/node
   - Progress bar with percentage
   - Elapsed time
   - Auto-updates from runtime API

2. **Add Stage Mapping** (30m)
   - WorkflowStatus → Display name
   - Colors per stage
   - Icons per stage

3. **Integrate with Dashboard** (30m)
   - Show in investigation details
   - Show in dashboard when running
   - Highlight active investigation

### Success Metrics

- Progress bar updates every 2s
- Correct percentages shown
- Current node labeled correctly
- Smooth animation (no jumps)

---

## Phase 13: Pipeline Visualization ⏳ QUEUED

**Est. Duration**: 3 hours  
**Blocker**: Phase 12 complete  
**Focus**: Show data flow through services  

### What Phase 13 Will Do

Visualize the complete data pipeline from attack simulator through all services.

### Pipeline Diagram

```
┌──────────────────┐
│ Attack Simulator │
│    (Running)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Kafka Event Bus  │
│  (3 msgs queued) │
└────────┬─────────┘
         │
         ├─────────────────────┐
         ▼                     ▼
    ┌────────────┐       ┌──────────────┐
    │ Ingestion  │       │  Evidence    │
    │ (Complete) │       │  (Processing)│
    └────┬───────┘       └──────┬───────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌──────────────────────┐
         │   Investigation      │
         │   Agent (Running)    │
         │   Node: Hypothesis   │
         │   Progress: 65%      │
         └──────────┬───────────┘
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
    ┌─────────────┐     ┌──────────┐
    │ Case Builder│     │ AI Report │
    │  (Queued)   │     │  (Queued) │
    └─────────────┘     └──────────┘
```

### Tasks

1. **Create Pipeline Component** (1h)
   - Location: `frontend/src/components/PipelineFlow.tsx`
   - Shows all services in chain
   - Highlights current stage
   - Color codes status

2. **Add Status Indicators** (1h)
   - Completed: ✅ Green
   - Running: 🔄 Blue
   - Queued: ⏳ Yellow
   - Failed: ❌ Red

3. **Integrate with Dashboard** (1h)
   - Show in investigation details
   - Show in dashboard
   - Update from runtime API

### Success Metrics

- Pipeline renders correctly
- Status updates in real-time
- Clear data flow visualization
- No performance impact

---

## Phase 14: Health Synchronization ⏳ QUEUED

**Est. Duration**: 1 hour  
**Blocker**: Phase 4 complete  
**Focus**: Show actual system health  

### What Phase 14 Will Do

Display real system health from /api/v1/platform/health instead of hardcoded values.

### Health Dashboard

```
System Health Status
══════════════════════════════════════════════════════

Service        Status    Latency    CPU    Memory    Updated
─────────────────────────────────────────────────────────
Kafka          ✅ UP     12ms       8%     42%       10s ago
Gateway        ✅ UP     8ms        5%     28%        8s ago
Investigation  ✅ UP     15ms       12%    56%        7s ago
Evidence       ✅ UP     22ms       18%    64%        5s ago
Threat         ✅ UP     18ms       10%    51%        3s ago
Knowledge      ✅ UP     25ms       14%    58%        2s ago
Graph          ⚠️  WARN  180ms      35%    78%       15s ago
Memory         ✅ UP     8ms        3%     48%        1s ago
Case           ✅ UP     12ms       6%     38%        9s ago
AI Report      ✅ UP     42ms       20%    62%        4s ago
Execution      ✅ UP     16ms       7%     44%        6s ago
ServiceNow     ✅ UP     85ms       15%    52%        11s ago
Neo4j          ✅ UP     9ms        25%    72%        2s ago
Redis          ✅ UP     2ms        1%     24%        3s ago
PostgreSQL     ✅ UP     5ms        12%    68%        5s ago
NVIDIA NIM     ✅ UP     120ms      45%    89%        1s ago
```

### Tasks

1. **Query Health API** (30m)
   - GET /api/v1/platform/health
   - Parse response
   - Calculate status indicators

2. **Update Health Component** (30m)
   - Remove hardcoded values
   - Bind to live API
   - Auto-refresh every 15s

### Success Metrics

- All service statuses correct
- Updates every 15 seconds
- Color coding works
- No hardcoded health data

---

## Phase 15: End-to-End Validation ⏳ QUEUED

**Est. Duration**: 4 hours  
**Blocker**: All phases 1-14 complete  
**Focus**: Validate complete platform integration  

### What Phase 15 Will Do

Run through all 6 attack scenarios end-to-end and verify the complete data flow works automatically.

### Validation Scenarios

1. **Credential Stuffing**
   - Start scenario
   - Watch investigation execute
   - Verify case created
   - Verify report generated
   - Verify execution planned
   - Verify ServiceNow incident

2. **Account Takeover**
   - Same as above

3. **Password Spray**
   - Same as above

4. **Money Mule**
   - Same as above

5. **Insider Threat**
   - Same as above

6. **Ransomware**
   - Same as above

### Validation Checklist

For each scenario:

- [ ] Simulator starts without errors
- [ ] Kafka events published (visible in logs)
- [ ] Investigation created (visible in frontend)
- [ ] Agent executes all 14 nodes (logs show all nodes)
- [ ] Timeline grows as agent executes (updates in real-time)
- [ ] Graph evolves (relationships appear)
- [ ] Progress bar updates (0→100%)
- [ ] Confidence increases (shown in runtime state)
- [ ] Hypotheses generated (shown in investigation)
- [ ] Case created (visible in cases view)
- [ ] AI Report generated (visible in reports)
- [ ] Execution plan created (visible in execution)
- [ ] ServiceNow incident created (integration working)
- [ ] No manual refresh needed (everything auto-updates)
- [ ] No errors in logs
- [ ] No console errors in browser

### Test Implementation

```bash
#!/bin/bash
# tests/e2e_phase15.sh

SCENARIOS=("credential_stuffing" "account_takeover" "password_spray" "money_mule" "insider_threat" "ransomware")

for scenario in "${SCENARIOS[@]}"; do
    echo "Testing: $scenario"
    
    # Start scenario
    curl -X POST http://localhost:8080/api/v1/simulations/run \
        -H "Content-Type: application/json" \
        -d "{\"scenario\": \"$scenario\"}"
    
    # Wait for completion (max 5 minutes)
    for i in {1..300}; do
        status=$(curl -s http://localhost:8080/api/v1/investigations \
            | jq -r '.[-1].state')
        
        if [ "$status" == "CLOSED" ]; then
            echo "  ✅ COMPLETED in ${i}s"
            break
        fi
        
        sleep 1
    done
    
    # Verify all components executed
    docker logs investigation-service | grep "workflow_execution_completed" | tail -1
    docker logs case-service | grep "investigation.completed" | tail -1
    docker logs ai-report-service | grep "investigation.completed" | tail -1
    docker logs execution-service | grep "investigation.completed" | tail -1
done

echo ""
echo "All scenarios validated ✅"
```

### Success Criteria

- All 6 scenarios complete successfully
- Complete data flow from simulator to ServiceNow
- All UIs update automatically
- No manual intervention required
- No errors in logs
- Performance acceptable (< 2min per scenario)

---

## Post-Phase 15: Production Readiness

Once Phase 15 passes, the Lokii platform is ready for:

1. **Load Testing**
   - Multiple concurrent investigations
   - High-volume event throughput

2. **Persistence Upgrade**
   - Replace in-memory storage with PostgreSQL
   - Implement proper checkpointing

3. **Monitoring & Observability**
   - Add detailed metrics
   - Add tracing
   - Add alerting

4. **Security Hardening**
   - Add auth/authz
   - Add encryption
   - Add rate limiting

5. **Documentation**
   - API documentation
   - Operation guides
   - Troubleshooting guides

---

## Critical Path to Completion

```
Phase 1 ✅ (Done)
  │
  ├─→ Phase 2 (Verify nodes execute)
  │     │
  │     ├─→ Phase 3 (Runtime state tracking)
  │     │     │
  │     │     ├─→ Phase 4 (Runtime API)
  │     │     │
  │     │     └─→ Phase 5 (Timeline API)
  │     │     │
  │     │     └─→ Phase 6 (Graph API)
  │     │
  │     ├─→ Phase 7 (Frontend: Replace mock with API calls)
  │     │     │
  │     │     ├─→ Phase 8 (Wire simulator button)
  │     │     │
  │     │     ├─→ Phase 9 (Add polling infrastructure)
  │     │     │
  │     │     ├─→ Phase 10 (Make dashboard live)
  │     │     │
  │     │     ├─→ Phase 11 (Make workspace live)
  │     │     │
  │     │     ├─→ Phase 12 (Progress visualization)
  │     │     │
  │     │     └─→ Phase 13 (Pipeline visualization)
  │     │
  │     └─→ Phase 14 (Health synchronization)
  │
  └─→ Phase 15 (End-to-end validation)
        │
        └─→ Production Ready! 🚀
```

---

## Progress Dashboard

| Phase | Status | Files | Hours | Start Date | End Date |
|-------|--------|-------|-------|-----------|----------|
| 1 | ✅ COMPLETE | 4 | 2 | 2024-07-16 | 2024-07-16 |
| 2 | ⏳ QUEUED | - | 5 | TBD | TBD |
| 3 | ⏳ QUEUED | - | 4 | TBD | TBD |
| 4 | ⏳ QUEUED | - | 2 | TBD | TBD |
| 5 | ⏳ QUEUED | - | 3 | TBD | TBD |
| 6 | ⏳ QUEUED | - | 3 | TBD | TBD |
| 7 | ⏳ QUEUED | - | 10 | TBD | TBD |
| 8 | ⏳ QUEUED | - | 2 | TBD | TBD |
| 9 | ⏳ QUEUED | - | 3 | TBD | TBD |
| 10 | ⏳ QUEUED | - | 4 | TBD | TBD |
| 11 | ⏳ QUEUED | - | 5 | TBD | TBD |
| 12 | ⏳ QUEUED | - | 2 | TBD | TBD |
| 13 | ⏳ QUEUED | - | 3 | TBD | TBD |
| 14 | ⏳ QUEUED | - | 1 | TBD | TBD |
| 15 | ⏳ QUEUED | - | 4 | TBD | TBD |
| **TOTAL** | **7% DONE** | **4** | **52 hours** | 2024-07-16 | TBD |

---

## Next Steps

✅ **Phase 1 Complete**: Investigation Agent is now active in the Kafka pipeline  
⏳ **Phase 2 Awaiting**: Verify all 14 nodes execute correctly  

**To proceed**:

```bash
# 1. Deploy Phase 1 code
git add .
git commit -m "Phase 1: Investigation Agent Activation"
git push

# 2. Rebuild and restart
docker compose down
docker compose build --no-cache  
docker compose up -d

# 3. Monitor execution
docker logs -f investigation-service | grep -E "candidate_ingested|workflow_execution"

# 4. When Phase 1 verified, begin Phase 2
# See: PHASE_2_PREPARATION_GUIDE.md
```

**Estimated Total Timeline**: 52 implementation hours + testing = ~2 weeks with focused effort

**Target Completion**: Lokii becomes a fully autonomous, real-time investigation platform
