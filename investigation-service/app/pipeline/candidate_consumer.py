from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Optional
from app.core.logger import get_logger
from app.schemas.candidate import CandidateInput
from app.services.investigation_manager import InvestigationManager
from app.events.kafka import KafkaProducer
from app.config.settings import settings
from app.agent.investigation_orchestrator import InvestigationOrchestrator
from app.agent.planner import InvestigationPlanner
from app.agent.tool_router import ToolRouter
from app.agent.checkpoint_manager import CheckpointManager
from app.agent.reasoning import ReasoningEngine
from app.agent.decision_engine import DecisionEngine
from app.agent.state_mapper import StateMapper
from app.agent.tools.mock_tools import mock_tool_set

logger = get_logger("candidate_pipeline")


class CandidatePipeline:
    """Kafka candidate consumer that invokes the Investigation Agent LangGraph workflow."""
    
    def __init__(self, manager: InvestigationManager, publisher: KafkaProducer, 
                 context_builder: Optional[object] = None, snapshot_manager: Optional[object] = None):
        self.manager = manager
        self.publisher = publisher
        self.context_builder = context_builder
        self.snapshot_manager = snapshot_manager
        self._setup_agent_components()

    def _setup_agent_components(self) -> None:
        """Initialize LangGraph agent components once."""
        try:
            tools = mock_tool_set()
            self.tool_router = ToolRouter(tools)
            self.checkpoint_manager = CheckpointManager()
            self.reasoning_engine = ReasoningEngine()
            self.decision_engine = DecisionEngine()
            self.planner = InvestigationPlanner(self.tool_router)
            logger.info("agent_components_initialized")
        except Exception as exc:
            logger.error("agent_initialization_failed", extra={"error": str(exc)})
            raise

    async def handle(self, message):
        """Process Kafka candidate message through Investigation Agent."""
        try:
            raw = message.value()
            logger.info("candidate_message_received")
            payload = json.loads(raw.decode() if isinstance(raw, (bytes, bytearray)) else raw)
            candidate = CandidateInput.model_validate(payload)
            logger.info("candidate_parsed", extra={"candidate_id": candidate.candidate_id, "pattern": candidate.pattern_name})
            
            # Step 1: Add hypothesis/evidence to Investigation (state preparation)
            investigation = self.manager.process(candidate)
            logger.info("candidate_ingested", extra={
                "investigation_id": investigation.investigation_id,
                "pattern": candidate.pattern_name,
            })
            
            # Step 2: Convert to InvestigationState for LangGraph
            agent_state = StateMapper.to_agent_state(investigation, investigation.metadata.tenant_id)
            
            # Step 3: Create orchestrator and execute workflow
            orchestrator = InvestigationOrchestrator(
                self.tool_router,
                self.planner.build()
            )
            orchestrator.checkpoints = self.checkpoint_manager
            orchestrator.reasoning = self.reasoning_engine
            orchestrator.decision = self.decision_engine
            
            logger.info("workflow_execution_starting", extra={
                "investigation_id": investigation.investigation_id,
                "initial_status": agent_state.workflow_status.value,
            })
            
            # Step 4: Execute the workflow
            final_state = orchestrator.start(agent_state)
            
            logger.info("workflow_execution_completed", extra={
                "investigation_id": investigation.investigation_id,
                "final_status": final_state.workflow_status.value,
                "duration_ms": sum(
                    (exec.duration_ms or 0) for exec in final_state.node_executions
                ),
                "node_count": len(final_state.node_executions),
            })
            
            # Step 5: Update Investigation with workflow results
            investigation = StateMapper.from_agent_state(final_state, investigation)
            self.manager.repository.save(investigation)
            
            # Step 6: Publish lifecycle events
            timestamp = datetime.now(timezone.utc).isoformat()
            self.publisher.publish_investigation(settings.producer_topic, "INVESTIGATION_ACTIVE", investigation, timestamp)
            self.publisher.publish_investigation(settings.updated_topic, "INVESTIGATION_UPDATED", investigation, timestamp)
            
            # Step 7: Publish completion event if workflow completed successfully
            if final_state.workflow_status.value == "COMPLETED":
                context = None
                if self.context_builder:
                    context = self.context_builder.build(investigation)
                
                snapshot = None
                if self.snapshot_manager:
                    try:
                        snapshot = self.snapshot_manager.latest(investigation.investigation_id)
                    except (KeyError, AttributeError):
                        pass
                
                self.publisher.publish_completed(
                    settings.completed_topic,
                    investigation,
                    context,
                    snapshot
                )
                logger.info("investigation_completed_published", extra={
                    "investigation_id": investigation.investigation_id,
                    "completion_timestamp": timestamp,
                })
            
            # Step 8: Handle failure/rollback scenarios
            if final_state.workflow_status.value == "FAILED":
                logger.error("workflow_execution_failed", extra={
                    "investigation_id": investigation.investigation_id,
                    "last_node": final_state.current_node,
                    "failure_count": final_state.failure_count,
                })
                self.publisher.publish_investigation(
                    settings.updated_topic,
                    "INVESTIGATION_FAILED",
                    investigation,
                    timestamp
                )
            elif final_state.workflow_status.value == "ROLLED_BACK":
                logger.info("workflow_rolled_back", extra={
                    "investigation_id": investigation.investigation_id,
                    "checkpoint_id": final_state.checkpoint_id,
                })
                self.publisher.publish_investigation(
                    settings.updated_topic,
                    "INVESTIGATION_ROLLED_BACK",
                    investigation,
                    timestamp
                )
        except Exception as exc:
            logger.error("candidate_processing_failed", extra={"error": str(exc), "exception_type": type(exc).__name__})
