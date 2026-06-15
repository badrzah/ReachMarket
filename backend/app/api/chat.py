import json
import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
import asyncpg
import httpx

from backend.app.db.connection import get_db
from backend.app.config import settings
from shared.schemas import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(
    body: ChatRequest,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db),
):
    """Chat endpoint — streams agent responses via SSE."""
    company_id = request.state.company_id
    user_id = request.state.user_id

    agent_payload = {
        "company_id": company_id,
        "user_id": user_id,
        "session_id": str(body.session_id) if body.session_id else None,
        "message": body.message,
        "mode": "chat",
    }

    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST", f"{settings.agents_url}/chat", json=agent_payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            # Agents service already emits "data: ..." lines
                            # Forward them as-is (don't double-wrap)
                            yield f"{line}\n\n"
        except httpx.ConnectError:
            # Fallback: return a simple response if agents service is down
            fallback = json.dumps({
                "event": "agent_output",
                "agent": "orchestrator",
                "message": "The AI agent service is currently starting up. Please try again in a moment.",
                "data": {"response": "Service temporarily unavailable. Please try again shortly."},
            })
            yield f"data: {fallback}\n\n"
            done = json.dumps({"event": "done"})
            yield f"data: {done}\n\n"
        except Exception as exc:
            error_data = json.dumps({"event": "error", "message": str(exc)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
