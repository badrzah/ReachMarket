"""Tests for orchestrator node routing logic."""

import uuid
import pytest
from unittest.mock import AsyncMock, patch
from shared.schemas import (
    ResearchReport, GTMStrategy, GTMMotion, CompanyProfile,
    MarketSize, ICPProfile, ValueProp, ContentAsset, ContentType,
)


def _make_state(**kwargs):
    """Create a GTMState with given overrides."""
    from agents.app.graph.state import GTMState
    defaults = {
        "session_id": uuid.uuid4(),
        "company_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "messages": [{"role": "user", "content": "Generate a GTM strategy"}],
        "metadata": {"company_profile": {"name": "TestCo", "industry": "SaaS", "stage": "seed", "description": "Test"}},
    }
    defaults.update(kwargs)
    return GTMState(**defaults)


def _make_research_report():
    return ResearchReport(
        company_profile=CompanyProfile(name="TestCo", industry="SaaS", stage="seed", description="Test"),
        market_size=MarketSize(tam="$1B", sam="$200M", som="$20M", source="Test", year=2025),
        competitors=[], segments=[],
        icp=ICPProfile(
            title="VP Sales", industry="SaaS", company_size="50-200",
            budget_range="$50K-$100K", pain_points=["pain"], goals=["grow"],
            buying_committee=["CEO"], disqualifiers=["no budget"],
        ),
        signals=[], sources=[],
    )


def _make_strategy():
    return GTMStrategy(
        motion=GTMMotion.SLG,
        icp=ICPProfile(
            title="VP Sales", industry="SaaS", company_size="50-200",
            budget_range="$50K-$100K", pain_points=["pain"], goals=["grow"],
            buying_committee=["CEO"], disqualifiers=["no budget"],
        ),
        value_proposition=ValueProp(
            headline="Test", subheadline="Test", proof_points=[], differentiators=[],
        ),
        channels=[], battlecards=[], growth_loops=[], ninety_day_plan=[],
        positioning_statement="Test positioning",
    )


class TestOrchestratorNode:
    """Test orchestrator routing logic."""

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.orchestrator.ChatOpenAI")
    async def test_routes_to_research_when_no_report(self, mock_llm_cls):
        """Without research report, should route to research."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = AsyncMock(content="Starting research")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.orchestrator import orchestrator_node

        state = _make_state(research_report=None, gtm_strategy=None)
        result = await orchestrator_node(state)

        assert result.current_agent == "orchestrator"
        assert result.metadata.get("routing") == "research"

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.orchestrator.ChatOpenAI")
    async def test_routes_to_content_when_strategy_exists(self, mock_llm_cls):
        """With strategy, should route to content."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = AsyncMock(content="Generating content")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.orchestrator import orchestrator_node

        state = _make_state(
            research_report=_make_research_report(),
            gtm_strategy=_make_strategy(),
        )
        result = await orchestrator_node(state)

        assert result.current_agent == "orchestrator"
        assert result.metadata.get("routing") == "content"

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.orchestrator.ChatOpenAI")
    async def test_routes_to_strategy_with_research_no_strategy(self, mock_llm_cls):
        """With research but no strategy, should route to strategy."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = AsyncMock(content="Building strategy")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.orchestrator import orchestrator_node

        state = _make_state(
            research_report=_make_research_report(),
            gtm_strategy=None,
        )
        result = await orchestrator_node(state)

        assert result.current_agent == "orchestrator"
        assert result.metadata.get("routing") == "strategy"

    @pytest.mark.asyncio
    async def test_falls_back_on_llm_error(self):
        """Should use rule-based routing when LLM fails."""
        with patch("agents.app.graph.nodes.orchestrator.ChatOpenAI") as mock_cls:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("API error")
            mock_cls.return_value = mock_llm

            from agents.app.graph.nodes.orchestrator import orchestrator_node

            state = _make_state(research_report=None)
            result = await orchestrator_node(state)

            assert result.current_agent == "orchestrator"
            # Should still set routing via rule-based fallback
            assert result.metadata.get("routing") is not None
