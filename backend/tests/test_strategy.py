"""Tests for strategy service and API endpoints."""

import uuid
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


class TestStrategyService:
    """Unit tests for strategy service functions."""

    @pytest.mark.asyncio
    async def test_create_strategy(self):
        """Test creating a new strategy record."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        mock_row = {
            "id": uuid.uuid4(),
            "company_id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "session_id": uuid.uuid4(),
            "status": "generating",
            "payload": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_conn.fetchrow.return_value = mock_row

        result = await strategy_service.create_strategy(
            mock_conn,
            str(mock_row["company_id"]),
            str(mock_row["user_id"]),
            mock_row["session_id"],
        )

        assert result["status"] == "generating"
        assert result["payload"] is None
        mock_conn.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_strategy(self):
        """Test fetching a strategy by ID."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        strategy_id = uuid.uuid4()
        mock_row = {
            "id": strategy_id,
            "company_id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "session_id": uuid.uuid4(),
            "status": "complete",
            "payload": {"motion": "sales_led_growth"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_conn.fetchrow.return_value = mock_row

        result = await strategy_service.get_strategy(mock_conn, str(strategy_id))
        assert result is not None
        assert result["status"] == "complete"

    @pytest.mark.asyncio
    async def test_get_strategy_not_found(self):
        """Test fetching a non-existent strategy returns None."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = None

        result = await strategy_service.get_strategy(mock_conn, str(uuid.uuid4()))
        assert result is None

    @pytest.mark.asyncio
    async def test_list_strategies(self):
        """Test listing strategies for a company."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        mock_rows = [
            {
                "id": uuid.uuid4(),
                "company_id": uuid.uuid4(),
                "user_id": uuid.uuid4(),
                "session_id": uuid.uuid4(),
                "status": "complete",
                "payload": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "id": uuid.uuid4(),
                "company_id": uuid.uuid4(),
                "user_id": uuid.uuid4(),
                "session_id": uuid.uuid4(),
                "status": "generating",
                "payload": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        mock_conn.fetch.return_value = mock_rows

        result = await strategy_service.list_strategies(mock_conn)
        assert len(result) == 2
        assert result[0]["status"] == "complete"

    @pytest.mark.asyncio
    async def test_update_strategy_status(self):
        """Test updating strategy status."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        strategy_id = str(uuid.uuid4())

        await strategy_service.update_strategy_status(
            mock_conn, strategy_id, "complete", {"motion": "slg"}
        )
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_strategy_status_without_payload(self):
        """Test updating strategy status without payload."""
        from backend.app.services import strategy_service

        mock_conn = AsyncMock()
        strategy_id = str(uuid.uuid4())

        await strategy_service.update_strategy_status(
            mock_conn, strategy_id, "failed"
        )
        mock_conn.execute.assert_called_once()
