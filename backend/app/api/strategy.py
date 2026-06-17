import json
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import asyncpg

from backend.app.db.connection import get_db_tenant, get_pool
from backend.app.services import strategy_service
from shared.schemas import StrategyGenerateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategy", tags=["strategy"])


@router.post("/generate")
async def generate_strategy(
    body: StrategyGenerateRequest,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Trigger LangGraph pipeline. Creates a strategy row, dispatches to agents."""
    company_id = request.state.company_id
    user_id = request.state.user_id
    session_id = uuid.uuid4()

    # Create strategy record in DB
    strategy = await strategy_service.create_strategy(
        conn, company_id, user_id, session_id
    )

    return {
        "session_id": str(session_id),
        "strategy_id": strategy["id"],
        "status": "generating",
    }


@router.get("/generate/stream")
async def stream_strategy(
    session_id: str,
    strategy_id: str,
    token: str,
    company_profile: str = "null",
    additional_context: str = "",
    request: Request = None,
):
    """SSE endpoint that proxies agent events to the browser.
    After the stream completes, the final result is saved to the strategy record.
    """
    from jose import jwt, JWTError
    from backend.app.config import settings

    # Validate JWT from query param (SSE can't send headers)
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        company_id = payload.get("company_id")
        user_id = payload.get("sub")
        if not company_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Parse company_profile from JSON string
    try:
        profile_data = json.loads(company_profile) if company_profile and company_profile != "null" else {}
    except json.JSONDecodeError:
        profile_data = {}

    pool = get_pool()

    async def event_generator():
        final_payload = None
        try:
            async for line in strategy_service.invoke_agents_stream(
                company_id=company_id,
                user_id=user_id,
                session_id=session_id,
                company_profile=profile_data,
                additional_context=additional_context or None,
            ):
                yield f"{line}\n\n"
                # Track agent_output for strategy agent to capture final payload
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        event_type = data.get("event")
                        if event_type == "agent_output" and data.get("agent") == "strategy":
                            final_payload = data.get("data")
                    except json.JSONDecodeError:
                        pass

            # Stream completed successfully — update strategy record
            async with pool.acquire() as conn:
                await conn.execute(
                    "SELECT set_config('app.current_company_id', $1, TRUE)",
                    company_id,
                )
                await strategy_service.update_strategy_status(
                    conn, strategy_id, "complete", final_payload
                )
        except Exception as exc:
            logger.error("Strategy stream error: %s", exc)
            error_data = json.dumps({"event": "error", "message": str(exc)})
            yield f"data: {error_data}\n\n"
            # Update strategy to failed
            try:
                async with pool.acquire() as conn:
                    await conn.execute(
                        "SELECT set_config('app.current_company_id', $1, TRUE)",
                        company_id,
                    )
                    await strategy_service.update_strategy_status(
                        conn, strategy_id, "failed"
                    )
            except Exception as db_exc:
                logger.error("Failed to update strategy status: %s", db_exc)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/")
async def list_strategies(
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """List all strategies for the current company."""
    strategies = await strategy_service.list_strategies(conn, request.state.company_id)
    return {"strategies": strategies, "total": len(strategies)}


@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db_tenant),
):
    """Fetch a single strategy by ID."""
    strategy = await strategy_service.get_strategy(conn, strategy_id, request.state.company_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy
