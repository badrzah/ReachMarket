import os
import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from agents.app.config import settings
from shared.schemas import AgentEventType, AgentEvent

logger = logging.getLogger(__name__)

# ── LangSmith setup (only when API key is actually configured) ──────────
try:
    if settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        logger.info("LangSmith tracing enabled (project=%s)", settings.langsmith_project)
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("LangSmith tracing disabled (no API key)")
except Exception as exc:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    logger.warning("LangSmith env setup failed: %s — tracing disabled", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from agents.app.graph.graph import graph  # noqa: F401 — validate graph compiles
    logger.info("LangGraph agent graph compiled successfully")
    yield

app = FastAPI(title="ReachGTM Agents", version="0.1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware,
    allow_origins=[
        "https://reachgtm-frontend.badrpcc.workers.dev",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Attach a unique request ID to every request for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info("request_id=%s method=%s path=%s", request_id, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


class RunRequest(BaseModel):
    company_id: str
    user_id: str
    session_id: Optional[str] = None
    company_profile: Optional[dict] = None
    additional_context: Optional[str] = None
    content_types: Optional[list[str]] = None
    count_per_type: Optional[int] = 3
    message: Optional[str] = None
    mode: Optional[str] = "full"  # full, content_only, chat


@app.get("/health")
async def health():
    return {"service": "agents", "status": "ok"}


@app.post("/run")
@app.post("/run")
async def run(body: RunRequest):
    """Invoke the LangGraph pipeline synchronously and return the result."""
    from agents.app.graph.graph import graph
    from agents.app.graph.state import GTMState

    # Build initial state
    state = GTMState(
        session_id=uuid.UUID(body.session_id) if body.session_id else uuid.uuid4(),
        company_id=uuid.UUID(body.company_id),
        user_id=uuid.UUID(body.user_id),
        messages=[{"role": "user", "content": body.message or "Generate GTM strategy"}],
        metadata={
            "company_profile": body.company_profile or {},
            "additional_context": body.additional_context,
            "content_types": body.content_types or ["cold_email", "linkedin_post"],
            "count_per_type": body.count_per_type or 3,
            "mode": body.mode,
        },
    )

    try:
        result = await graph.ainvoke(state)

        # Serialize result (LangGraph returns dict from ainvoke)
        session_id = result.get("session_id") or result.get("session_id")
        if isinstance(session_id, uuid.UUID):
            session_id = str(session_id)

        response = {
            "session_id": session_id,
            "status": "complete",
            "current_agent": result.get("current_agent"),
        }

        research_report = result.get("research_report")
        if research_report:
            if hasattr(research_report, "model_dump"):
                response["research_report"] = research_report.model_dump(mode="json")
            else:
                response["research_report"] = research_report

        gtm_strategy = result.get("gtm_strategy")
        if gtm_strategy:
            if hasattr(gtm_strategy, "model_dump"):
                response["gtm_strategy"] = gtm_strategy.model_dump(mode="json")
                response["payload"] = gtm_strategy.model_dump(mode="json")
            else:
                response["gtm_strategy"] = gtm_strategy
                response["payload"] = gtm_strategy

        content_assets = result.get("content_assets")
        if content_assets:
            response["content_assets"] = [
                a.model_dump(mode="json") if hasattr(a, "model_dump") else a
                for a in content_assets
            ]

        errors = result.get("errors")
        if errors:
            response["errors"] = errors

        return response

    except Exception as exc:
        logger.error("Graph execution failed: %s", exc, exc_info=True)
        return {"status": "failed", "error": str(exc)}


@app.get("/run/stream")
async def run_stream(
    session_id: str,
    company_id: str,
    user_id: str,
    company_profile: str = "{}",
    additional_context: str = "",
):
    """SSE streaming endpoint — runs graph and emits events per node."""
    from agents.app.graph.graph import graph
    from agents.app.graph.state import GTMState

    try:
        profile_data = json.loads(company_profile)
    except json.JSONDecodeError:
        profile_data = {}

    state = GTMState(
        session_id=uuid.UUID(session_id) if session_id else uuid.uuid4(),
        company_id=uuid.UUID(company_id),
        user_id=uuid.UUID(user_id),
        messages=[{"role": "user", "content": "Generate GTM strategy"}],
        metadata={
            "company_profile": profile_data,
            "additional_context": additional_context or None,
            "content_types": ["cold_email", "linkedin_post"],
            "count_per_type": 3,
        },
    )

    async def event_generator():
        try:
            # Stream graph execution node by node
            previous_agent = None
            async for event in graph.astream(state, stream_mode="values"):
                current_agent = event.get("current_agent") if isinstance(event, dict) else event.current_agent

                if current_agent and current_agent != previous_agent:
                    # Emit agent_complete for previous agent
                    if previous_agent:
                        complete_event = AgentEvent(
                            event=AgentEventType.AGENT_COMPLETE,
                            agent=previous_agent,
                            message=f"{previous_agent} completed",
                        )
                        yield f"data: {complete_event.model_dump_json()}\n\n"

                    # Emit agent_start for current agent
                    start_event = AgentEvent(
                        event=AgentEventType.AGENT_START,
                        agent=current_agent,
                        message=f"{current_agent} started processing",
                    )
                    yield f"data: {start_event.model_dump_json()}\n\n"

                    # Emit output data if available
                    output_data = None
                    if current_agent == "research":
                        rr = event.get("research_report") if isinstance(event, dict) else event.research_report
                        if rr:
                            output_data = rr.model_dump(mode="json") if hasattr(rr, "model_dump") else rr
                    elif current_agent == "strategy":
                        gs = event.get("gtm_strategy") if isinstance(event, dict) else event.gtm_strategy
                        if gs:
                            output_data = gs.model_dump(mode="json") if hasattr(gs, "model_dump") else gs
                    elif current_agent in ("content", "brand_alignment"):
                        ca = event.get("content_assets") if isinstance(event, dict) else event.content_assets
                        if ca:
                            output_data = [a.model_dump(mode="json") if hasattr(a, "model_dump") else a for a in ca]

                    if output_data:
                        output_event = AgentEvent(
                            event=AgentEventType.AGENT_OUTPUT,
                            agent=current_agent,
                            data=output_data,
                        )
                        yield f"data: {output_event.model_dump_json()}\n\n"

                    previous_agent = current_agent

            # Final complete event
            if previous_agent:
                complete_event = AgentEvent(
                    event=AgentEventType.AGENT_COMPLETE,
                    agent=previous_agent,
                    message=f"{previous_agent} completed",
                )
                yield f"data: {complete_event.model_dump_json()}\n\n"

            # Done event
            done_event = AgentEvent(
                event=AgentEventType.DONE,
                message="All agents completed successfully",
            )
            yield f"data: {done_event.model_dump_json()}\n\n"

        except Exception as exc:
            logger.error("Streaming error: %s", exc, exc_info=True)
            error_event = AgentEvent(
                event=AgentEventType.ERROR,
                message=str(exc),
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/chat")
async def chat(body: RunRequest):
    """Chat endpoint — RAG-powered assistant with knowledge base context."""
    import asyncpg
    from openai import AsyncOpenAI
    from agents.app.config import settings as agent_settings

    async def retrieve_knowledge(query: str, company_id: str, top_k: int = 5) -> str:
        """Query pgvector for relevant document chunks."""
        try:
            openai_client = AsyncOpenAI(api_key=agent_settings.openai_api_key)
            embedding_resp = await openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query,
            )
            query_embedding = embedding_resp.data[0].embedding

            conn = await asyncpg.connect(agent_settings.database_url)
            try:
                rows = await conn.fetch(
                    """SELECT content, chunk_index, namespace
                       FROM document_chunks
                       WHERE company_id = $1::uuid
                       ORDER BY embedding <=> $2::vector
                       LIMIT $3""",
                    company_id, str(query_embedding), top_k,
                )
                if not rows:
                    return ""
                sections = []
                for r in rows:
                    doc_type = r["namespace"].split(":")[-1] if ":" in r["namespace"] else "document"
                    sections.append(f"[{doc_type}] {r['content']}")
                return "\n\n".join(sections)
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Knowledge retrieval failed: %s", exc)
            return ""

    async def event_generator():
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                api_key=settings.openai_api_key,
                max_tokens=1000,
                request_timeout=30,
            )

            # Retrieve relevant knowledge
            knowledge_context = ""
            if body.company_id:
                knowledge_context = await retrieve_knowledge(
                    body.message or "", str(body.company_id)
                )

            system_content = (
                "You are the ReachGTM AI assistant. Help users with their "
                "Go-To-Market strategy questions. Be concise, actionable, "
                "and data-driven in your responses."
            )
            if knowledge_context:
                system_content += (
                    "\n\nYou have access to the company's knowledge base documents. "
                    "Use the following information to provide more accurate, "
                    "context-aware answers:\n\n" + knowledge_context
                )

            response = await llm.ainvoke([
                SystemMessage(content=system_content),
                HumanMessage(content=body.message or "Hello"),
            ])

            output_event = AgentEvent(
                event=AgentEventType.AGENT_OUTPUT,
                agent="orchestrator",
                message=response.content,
                data={"response": response.content},
            )
            yield f"data: {output_event.model_dump_json()}\n\n"

            done_event = AgentEvent(
                event=AgentEventType.DONE,
                message="Chat response complete",
            )
            yield f"data: {done_event.model_dump_json()}\n\n"

        except Exception as exc:
            error_event = AgentEvent(
                event=AgentEventType.ERROR,
                message=str(exc),
            )
            yield f"data: {error_event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
