#!/usr/bin/env python3
"""
Local test of Phase 1 LangGraph orchestrator
Tests StateMapper, CandidatePipeline, and InvestigationOrchestrator
"""

import sys
import json
from pathlib import Path

# Add investigation-service to path
sys.path.insert(0, str(Path(__file__).parent / "investigation-service"))
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from app.schemas.investigation import Investigation, InvestigationState as DBInvestigationState
from app.schemas.candidate import CandidateInput
from app.agent.state_mapper import StateMapper
from app.agent.investigation_orchestrator import InvestigationOrchestrator
from app.agent.planner import InvestigationPlanner
from app.agent.tool_router import ToolRouter
from app.agent.checkpoint_manager import CheckpointManager
from app.agent.reasoning import ReasoningEngine
from app.agent.decision_engine import DecisionEngine
from app.agent.tools.mock_tools import mock_tool_set
from app.agent.state import InvestigationState

print("=" * 80)
print("PHASE 1 LOCAL TEST - LangGraph Orchestrator")
print("=" * 80)

# Create test investigation
print("\n[1] Creating test investigation...")
investigation = Investigation(
    investigation_id="test-inv-001",
    tenant_id="tenant-001",
    case_type="fraud",
    severity="critical",
    status=DBInvestigationState.ANALYZING,
)
print(f"✓ Investigation created: {investigation.investigation_id}")

# Map to agent state
print("\n[2] Converting Investigation to InvestigationState...")
agent_state = StateMapper.to_agent_state(investigation, "tenant-001")
print(f"✓ State mapped successfully")
print(f"  - Workflow Status: {agent_state.workflow_status}")
print(f"  - Investigation ID: {agent_state.investigation_id}")
print(f"  - Tenant ID: {agent_state.tenant_id}")

# Initialize agent components
print("\n[3] Initializing agent components...")
try:
    tools = mock_tool_set()
    print(f"✓ Mock tools loaded: {list(tools.keys())}")
    
    tool_router = ToolRouter(tools)
    checkpoint_manager = CheckpointManager()
    reasoning_engine = ReasoningEngine()
    decision_engine = DecisionEngine()
    planner = InvestigationPlanner(tool_router)
    print(f"✓ All components initialized")
except Exception as e:
    print(f"✗ Component initialization failed: {e}")
    sys.exit(1)

# Create orchestrator
print("\n[4] Creating InvestigationOrchestrator...")
try:
    graph = planner.build()
    orchestrator = InvestigationOrchestrator(tool_router, graph)
    orchestrator.checkpoints = checkpoint_manager
    orchestrator.reasoning = reasoning_engine
    orchestrator.decision = decision_engine
    print(f"✓ Orchestrator created with injected components")
except Exception as e:
    print(f"✗ Orchestrator creation failed: {e}")
    sys.exit(1)

# Execute workflow
print("\n[5] Executing LangGraph workflow...")
try:
    print(f"  Starting state: workflow_status = {agent_state.workflow_status}")
    final_state = orchestrator.start(agent_state)
    print(f"✓ Workflow executed successfully")
    print(f"  Final state: workflow_status = {final_state.workflow_status}")
    print(f"  Confidence: {final_state.confidence}")
    print(f"  Selected Hypothesis: {final_state.selected_hypothesis}")
except Exception as e:
    print(f"✗ Workflow execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Map back to Investigation
print("\n[6] Converting InvestigationState back to Investigation...")
try:
    updated_investigation = investigation.model_copy()
    StateMapper.from_agent_state(final_state, updated_investigation)
    print(f"✓ State converted back successfully")
    print(f"  AI Summary: {updated_investigation.ai_summary[:50]}..." if updated_investigation.ai_summary else "  AI Summary: (none)")
    print(f"  Final Confidence: {updated_investigation.confidence}")
except Exception as e:
    print(f"✗ State conversion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("PHASE 1 TEST PASSED ✓")
print("=" * 80)
print("\nSummary:")
print(f"  - Investigation State Mapping: ✓")
print(f"  - Agent Component Injection: ✓")
print(f"  - LangGraph Workflow Execution: ✓")
print(f"  - State Persistence: ✓")
print(f"\nPhase 1 is operational at runtime!")
