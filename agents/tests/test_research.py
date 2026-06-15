"""Tests for research node with mocked LLM."""

import uuid
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def _make_state(**kwargs):
    from agents.app.graph.state import GTMState
    defaults = {
        "session_id": uuid.uuid4(),
        "company_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "messages": [{"role": "user", "content": "Research my company"}],
        "metadata": {
            "company_profile": {
                "name": "TestCo",
                "industry": "SaaS",
                "stage": "seed",
                "description": "AI-powered sales automation platform",
            }
        },
    }
    defaults.update(kwargs)
    return GTMState(**defaults)


MOCK_RESEARCH_JSON = json.dumps({
    "company_profile": {
        "name": "TestCo", "industry": "SaaS", "stage": "seed",
        "description": "AI-powered sales automation platform",
    },
    "market_size": {"tam": "$5B", "sam": "$1B", "som": "$100M", "source": "Gartner", "year": 2025},
    "competitors": [
        {"name": "CompA", "positioning": "Market leader",
         "strengths": ["Brand"], "weaknesses": ["Slow innovation"]},
    ],
    "segments": [
        {"name": "Mid-Market", "description": "Growing SaaS companies",
         "size_estimate": "40%", "pain_points": ["scaling"],
         "buying_triggers": ["funding"]},
    ],
    "icp": {
        "title": "VP Sales", "industry": "SaaS", "company_size": "50-200",
        "budget_range": "$50K-$100K", "pain_points": ["low conversion"],
        "goals": ["increase revenue"], "buying_committee": ["CEO", "CRO"],
        "disqualifiers": ["no budget"],
    },
    "signals": [{"type": "funding", "description": "Series B funding surge", "relevance": "High"}],
    "sources": ["Gartner 2025 report"],
})


class TestResearchNode:
    """Test research node LLM integration."""

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.research.ChatOpenAI")
    async def test_generates_research_report(self, mock_llm_cls):
        """Test successful research report generation."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content=MOCK_RESEARCH_JSON)
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.research import research_node

        state = _make_state()
        result = await research_node(state)

        assert result.current_agent == "research"
        assert result.research_report is not None
        assert result.research_report.market_size.tam == "$5B"
        assert len(result.research_report.competitors) == 1
        assert result.research_report.icp.title == "VP Sales"

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.research.ChatOpenAI")
    async def test_falls_back_on_json_error(self, mock_llm_cls):
        """Test fallback when LLM returns invalid JSON."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content="This is not JSON at all")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.research import research_node

        state = _make_state()
        result = await research_node(state)

        assert result.current_agent == "research"
        assert result.research_report is not None  # Should use fallback
        assert result.research_report.company_profile.name == "TestCo"

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.research.ChatOpenAI")
    async def test_handles_llm_exception(self, mock_llm_cls):
        """Test graceful handling of LLM API errors."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("API rate limit")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.research import research_node

        state = _make_state()
        result = await research_node(state)

        assert result.current_agent == "research"
        assert result.research_report is not None  # Should use fallback

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.research.ChatOpenAI")
    async def test_handles_markdown_wrapped_json(self, mock_llm_cls):
        """Test parsing JSON wrapped in markdown code blocks."""
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(
            content=f"```json\n{MOCK_RESEARCH_JSON}\n```"
        )
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.research import research_node

        state = _make_state()
        result = await research_node(state)

        assert result.research_report is not None
        assert result.research_report.market_size.tam == "$5B"
