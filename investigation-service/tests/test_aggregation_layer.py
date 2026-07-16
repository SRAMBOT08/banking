from app.aggregation import IntelligenceAggregator
from app.agent.state import InvestigationState
from app.agent.tool_router import ToolRouter
from app.agent.tools.mock_tools import mock_tool_set


def test_mock_aggregation_collects_all_sources():
    state = InvestigationState.new("aggregation-test", "tenant")
    context = IntelligenceAggregator(ToolRouter(mock_tool_set())).aggregate(state)
    print(context.missing_information, context.merge_statistics)
    assert context.missing_information == []
    assert context.evidence_context.items
    assert context.knowledge_context.items
    assert context.threat_context.items
    assert context.historical_context.items
