import json
import uuid
import logging
from datetime import datetime
from typing import Optional

import asyncpg
import httpx

from backend.app.config import settings

logger = logging.getLogger(__name__)


async def create_strategy(
    conn: asyncpg.Connection,
    company_id: str,
    user_id: str,
    session_id: uuid.UUID,
) -> dict:
    """Insert a new strategy row with status='generating'."""
    row = await conn.fetchrow(
        """INSERT INTO strategies (company_id, user_id, session_id, status)
           VALUES ($1, $2, $3, 'generating')
           RETURNING id, company_id, user_id, session_id, status, payload, created_at, updated_at""",
        uuid.UUID(company_id),
        uuid.UUID(user_id),
        session_id,
    )
    return _row_to_dict(row)


async def get_strategy(conn: asyncpg.Connection, strategy_id: str, company_id: str) -> Optional[dict]:
    """Fetch a single strategy by ID (scoped to company)."""
    row = await conn.fetchrow(
        """SELECT id, company_id, user_id, session_id, status, payload, created_at, updated_at
           FROM strategies WHERE id = $1 AND company_id = $2""",
        uuid.UUID(strategy_id), uuid.UUID(company_id),
    )
    return _row_to_dict(row) if row else None


async def list_strategies(conn: asyncpg.Connection, company_id: str) -> list[dict]:
    """List all strategies for the current company."""
    rows = await conn.fetch(
        """SELECT id, company_id, user_id, session_id, status, payload, created_at, updated_at
           FROM strategies WHERE company_id = $1 ORDER BY created_at DESC""",
        uuid.UUID(company_id),
    )
    return [_row_to_dict(r) for r in rows]


async def update_strategy_status(
    conn: asyncpg.Connection,
    strategy_id: str,
    status: str,
    payload: Optional[dict] = None,
) -> None:
    """Update strategy status and optionally its payload."""
    if payload is not None:
        await conn.execute(
            """UPDATE strategies
               SET status = $1, payload = $2::jsonb, updated_at = NOW()
               WHERE id = $3""",
            status,
            json.dumps(payload),
            uuid.UUID(strategy_id),
        )
    else:
        await conn.execute(
            """UPDATE strategies SET status = $1, updated_at = NOW() WHERE id = $2""",
            status,
            uuid.UUID(strategy_id),
        )


async def invoke_agents_stream(
    company_id: str,
    user_id: str,
    session_id: str,
    company_profile: dict,
    additional_context: Optional[str] = None,
):
    """Stream SSE events from the agents service /run/stream endpoint."""
    params = {
        "company_id": company_id,
        "user_id": user_id,
        "session_id": session_id,
        "company_profile": json.dumps(company_profile),
    }
    if additional_context:
        params["additional_context"] = additional_context

    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "GET", f"{settings.agents_url}/run/stream", params=params
        ) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    yield line


async def delete_strategy(conn: asyncpg.Connection, strategy_id: str, company_id: str) -> bool:
    """Delete a strategy by ID (scoped to company). Returns True if deleted."""
    result = await conn.execute(
        "DELETE FROM strategies WHERE id = $1 AND company_id = $2",
        uuid.UUID(strategy_id), uuid.UUID(company_id),
    )
    return result != "DELETE 0"


def _row_to_dict(row: asyncpg.Record) -> dict:
    """Convert asyncpg Record to dict, serializing UUIDs and datetimes."""
    d = dict(row)
    for key, value in d.items():
        if isinstance(value, uuid.UUID):
            d[key] = str(value)
        elif isinstance(value, datetime):
            d[key] = value.isoformat()
        elif isinstance(value, str):
            # asyncpg sometimes returns JSONB as string instead of dict
            # Try to parse as JSON for known JSONB-containing columns
            if key in ("payload",):
                try:
                    parsed = json.loads(value)
                    d[key] = parsed
                except (json.JSONDecodeError, TypeError):
                    pass
    return d
