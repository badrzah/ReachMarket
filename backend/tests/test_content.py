"""Tests for content service functions."""

import uuid
import pytest
from unittest.mock import AsyncMock
from datetime import datetime


class TestContentService:
    """Unit tests for content service."""

    @pytest.mark.asyncio
    async def test_create_content_asset(self):
        """Test creating a content asset."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        mock_row = {
            "id": uuid.uuid4(),
            "company_id": uuid.uuid4(),
            "strategy_id": uuid.uuid4(),
            "content_type": "cold_email",
            "title": "Test Email",
            "body": "Hello, this is a test.",
            "validation_status": "pending",
            "brand_alignment_score": None,
            "created_at": datetime.utcnow(),
        }
        mock_conn.fetchrow.return_value = mock_row

        result = await content_service.create_content_asset(
            mock_conn,
            str(mock_row["company_id"]),
            str(mock_row["strategy_id"]),
            "cold_email",
            "Test Email",
            "Hello, this is a test.",
        )

        assert result["content_type"] == "cold_email"
        assert result["title"] == "Test Email"
        mock_conn.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_content_assets(self):
        """Test listing content assets."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {
                "id": uuid.uuid4(),
                "company_id": uuid.uuid4(),
                "strategy_id": uuid.uuid4(),
                "content_type": "cold_email",
                "title": "Email 1",
                "body": "Body 1",
                "validation_status": "approved",
                "brand_alignment_score": 0.85,
                "created_at": datetime.utcnow(),
            }
        ]

        result = await content_service.list_content_assets(mock_conn)
        assert len(result) == 1
        assert result[0]["validation_status"] == "approved"

    @pytest.mark.asyncio
    async def test_list_content_assets_with_filter(self):
        """Test listing with content type filter."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []

        result = await content_service.list_content_assets(
            mock_conn, content_type="linkedin_post"
        )
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_content_asset(self):
        """Test getting a single content asset."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        asset_id = uuid.uuid4()
        mock_conn.fetchrow.return_value = {
            "id": asset_id,
            "company_id": uuid.uuid4(),
            "strategy_id": uuid.uuid4(),
            "content_type": "linkedin_post",
            "title": "LinkedIn Post",
            "body": "Content here",
            "validation_status": "approved",
            "brand_alignment_score": 0.92,
            "created_at": datetime.utcnow(),
        }

        result = await content_service.get_content_asset(mock_conn, str(asset_id))
        assert result is not None
        assert result["content_type"] == "linkedin_post"

    @pytest.mark.asyncio
    async def test_get_content_asset_not_found(self):
        """Test getting non-existent asset returns None."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = None

        result = await content_service.get_content_asset(mock_conn, str(uuid.uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_bulk_create_content_assets(self):
        """Test bulk creating content assets."""
        from backend.app.services import content_service

        mock_conn = AsyncMock()
        company_id = str(uuid.uuid4())
        strategy_id = str(uuid.uuid4())

        mock_conn.fetchrow.return_value = {
            "id": uuid.uuid4(),
            "company_id": uuid.UUID(company_id),
            "strategy_id": uuid.UUID(strategy_id),
            "content_type": "cold_email",
            "title": "Email",
            "body": "Body",
            "validation_status": "approved",
            "brand_alignment_score": 0.8,
            "created_at": datetime.utcnow(),
        }

        # Mock transaction context manager
        mock_conn.transaction.return_value.__aenter__ = AsyncMock()
        mock_conn.transaction.return_value.__aexit__ = AsyncMock()

        assets = [
            {"title": "Email 1", "body": "Body 1", "type": "cold_email"},
            {"title": "Email 2", "body": "Body 2", "type": "cold_email"},
        ]

        result = await content_service.bulk_create_content_assets(
            mock_conn, company_id, strategy_id, assets
        )
        assert len(result) == 2
