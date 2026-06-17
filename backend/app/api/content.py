import logging

from fastapi import APIRouter, Depends, HTTPException, Request
import asyncpg

from backend.app.db.connection import get_db_tenant
from backend.app.services import content_service
from shared.schemas import ContentGenerateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/generate")
async def generate_content(
    body: ContentGenerateRequest,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Generate content assets via the agent pipeline and persist to DB."""
    company_id = request.state.company_id
    user_id = request.state.user_id

    # Call agents service to generate content
    import httpx
    from backend.app.config import settings

    agent_payload = {
        "company_id": company_id,
        "user_id": user_id,
        "session_id": str(body.strategy_id),
        "content_types": [ct.value for ct in body.content_types],
        "count_per_type": body.count_per_type,
        "mode": "content_only",
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(f"{settings.agents_url}/run", json=agent_payload)
            resp.raise_for_status()
            result = resp.json()
    except Exception as exc:
        logger.error("Content generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Agent service error: {str(exc)}")

    # Extract content assets from agent result
    raw_assets = result.get("content_assets", [])

    # Persist to DB
    assets = await content_service.bulk_create_content_assets(
        conn,
        company_id=company_id,
        strategy_id=str(body.strategy_id),
        assets=raw_assets,
    )

    return {"assets": assets, "total": len(assets)}


@router.get("/")
async def list_content(
    request: Request,
    content_type: str | None = None,
    strategy_id: str | None = None,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """List content assets for the current company with optional filters."""
    assets = await content_service.list_content_assets(
        conn, company_id=request.state.company_id, content_type=content_type, strategy_id=strategy_id
    )
    return {"assets": assets, "total": len(assets)}


@router.get("/{asset_id}")
async def get_content(
    asset_id: str,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Fetch a single content asset by ID."""
    asset = await content_service.get_content_asset(conn, asset_id, request.state.company_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Content asset not found")
    return asset
