import uuid
import logging
from datetime import datetime
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)


async def create_content_asset(
    conn: asyncpg.Connection,
    company_id: str,
    strategy_id: Optional[str],
    content_type: str,
    title: str,
    body: str,
    validation_status: str = "pending",
    brand_alignment_score: Optional[float] = None,
) -> dict:
    """Insert a new content asset."""
    row = await conn.fetchrow(
        """INSERT INTO content_assets
           (company_id, strategy_id, content_type, title, body, validation_status, brand_alignment_score)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           RETURNING id, company_id, strategy_id, content_type, title, body,
                     validation_status, brand_alignment_score, created_at""",
        uuid.UUID(company_id),
        uuid.UUID(strategy_id) if strategy_id else None,
        content_type,
        title,
        body,
        validation_status,
        brand_alignment_score,
    )
    return _row_to_dict(row)


async def list_content_assets(
    conn: asyncpg.Connection,
    company_id: str,
    content_type: Optional[str] = None,
    strategy_id: Optional[str] = None,
) -> list[dict]:
    """List content assets for the current company."""
    query = """SELECT id, company_id, strategy_id, content_type, title, body,
                      validation_status, brand_alignment_score, created_at
               FROM content_assets"""
    conditions = ["company_id = $1"]
    params = [uuid.UUID(company_id)]

    if content_type:
        params.append(content_type)
        conditions.append(f"content_type = ${len(params)}")
    if strategy_id:
        params.append(uuid.UUID(strategy_id))
        conditions.append(f"strategy_id = ${len(params)}")

    query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY created_at DESC"

    rows = await conn.fetch(query, *params)
    return [_row_to_dict(r) for r in rows]


async def get_content_asset(conn: asyncpg.Connection, asset_id: str, company_id: str) -> Optional[dict]:
    """Get a single content asset by ID (scoped to company)."""
    row = await conn.fetchrow(
        """SELECT id, company_id, strategy_id, content_type, title, body,
                  validation_status, brand_alignment_score, created_at
           FROM content_assets WHERE id = $1 AND company_id = $2""",
        uuid.UUID(asset_id), uuid.UUID(company_id),
    )
    return _row_to_dict(row) if row else None


async def bulk_create_content_assets(
    conn: asyncpg.Connection,
    company_id: str,
    strategy_id: Optional[str],
    assets: list[dict],
) -> list[dict]:
    """Bulk insert content assets from agent output."""
    created = []
    async with conn.transaction():
        for asset in assets:
            row = await conn.fetchrow(
                """INSERT INTO content_assets
                   (company_id, strategy_id, content_type, title, body,
                    validation_status, brand_alignment_score)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)
                   RETURNING id, company_id, strategy_id, content_type, title, body,
                             validation_status, brand_alignment_score, created_at""",
                uuid.UUID(company_id),
                uuid.UUID(strategy_id) if strategy_id else None,
                asset.get("type", asset.get("content_type", "cold_email")),
                asset["title"],
                asset["body"],
                asset.get("validation_status", "pending"),
                asset.get("brand_alignment_score"),
            )
            created.append(_row_to_dict(row))
    return created


def _row_to_dict(row: asyncpg.Record) -> dict:
    """Convert asyncpg Record to dict with serialized types."""
    d = dict(row)
    for key, value in d.items():
        if isinstance(value, uuid.UUID):
            d[key] = str(value)
        elif isinstance(value, datetime):
            d[key] = value.isoformat()
    return d
