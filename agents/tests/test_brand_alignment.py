"""Tests for brand alignment node."""

import uuid
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from shared.schemas import ContentAsset, ContentType, ValidationStatus


def _make_state(**kwargs):
    from agents.app.graph.state import GTMState
    defaults = {
        "session_id": uuid.uuid4(),
        "company_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "messages": [],
        "content_assets": [
            ContentAsset(
                type=ContentType.COLD_EMAIL,
                title="Test Email",
                body="Hey there, check out our product!",
                target_icp="SaaS",
            ),
        ],
    }
    defaults.update(kwargs)
    return GTMState(**defaults)


class TestBrandAlignmentNode:
    """Test brand alignment scoring and revision."""

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.brand_alignment._get_brand_context")
    @patch("agents.app.graph.nodes.brand_alignment.ChatOpenAI")
    async def test_approves_high_score_content(self, mock_llm_cls, mock_brand_ctx):
        """Content with high brand score should be approved."""
        mock_brand_ctx.return_value = "Brand: Professional, data-driven tone"

        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(
            content=json.dumps({"score": 0.92, "notes": "Great alignment", "needs_revision": False})
        )
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.brand_alignment import brand_alignment_node

        state = _make_state()
        result = await brand_alignment_node(state)

        assert result.current_agent == "brand_alignment"
        assert len(result.content_assets) == 1
        assert result.content_assets[0].brand_alignment_score >= 0.9
        assert result.content_assets[0].validation_status == ValidationStatus.APPROVED

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.brand_alignment._get_brand_context")
    @patch("agents.app.graph.nodes.brand_alignment.ChatOpenAI")
    async def test_revises_low_score_content(self, mock_llm_cls, mock_brand_ctx):
        """Content with low score should be revised."""
        mock_brand_ctx.return_value = "Brand: Professional tone"

        mock_llm = AsyncMock()
        # First call: low score, needs revision
        # Second call: revision
        # Third call: higher score
        mock_llm.ainvoke.side_effect = [
            MagicMock(content=json.dumps({"score": 0.5, "notes": "Too casual", "needs_revision": True})),
            MagicMock(content="Revised professional content here"),
            MagicMock(content=json.dumps({"score": 0.82, "notes": "Better alignment", "needs_revision": False})),
        ]
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.brand_alignment import brand_alignment_node

        state = _make_state()
        result = await brand_alignment_node(state)

        assert result.current_agent == "brand_alignment"
        assert result.content_assets[0].brand_alignment_score >= 0.7

    @pytest.mark.asyncio
    async def test_handles_no_content_assets(self):
        """Should handle empty content assets gracefully."""
        from agents.app.graph.nodes.brand_alignment import brand_alignment_node

        state = _make_state(content_assets=[])
        result = await brand_alignment_node(state)

        assert result.current_agent == "brand_alignment"
        assert len(result.content_assets) == 0

    @pytest.mark.asyncio
    @patch("agents.app.graph.nodes.brand_alignment._get_brand_context")
    @patch("agents.app.graph.nodes.brand_alignment.ChatOpenAI")
    async def test_auto_approves_on_llm_error(self, mock_llm_cls, mock_brand_ctx):
        """Should auto-approve with default score on LLM error."""
        mock_brand_ctx.return_value = "Brand: Professional"

        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("API error")
        mock_llm_cls.return_value = mock_llm

        from agents.app.graph.nodes.brand_alignment import brand_alignment_node

        state = _make_state()
        result = await brand_alignment_node(state)

        assert result.current_agent == "brand_alignment"
        assert result.content_assets[0].validation_status == ValidationStatus.APPROVED
        assert result.content_assets[0].brand_alignment_score == 0.75
