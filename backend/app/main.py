from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.db.connection import init_pool, close_pool, get_pool
from backend.app.middleware.tenant import TenantMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.api import auth, chat, strategy, content, knowledge
from pathlib import Path

CORS_ORIGINS = [
    "http://localhost:3000",
    "https://reachgtm-frontend.badrpcc.workers.dev",
    "https://reachgtm-frontend.pages.dev",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    pool = get_pool()
    async with pool.acquire() as conn:
        migration_path = Path(__file__).parent / "db" / "migrations" / "init.sql"
        if migration_path.exists():
            sql = migration_path.read_text()
            await conn.execute(sql)
    yield
    await close_pool()

app = FastAPI(title="ReachGTM Backend", version="0.1.0", lifespan=lifespan)

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import Headers

class CORSASGIMiddleware:
    """ASGI middleware for CORS. Runs at the outermost layer."""
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            origin = headers.get("origin", "")
            if scope["method"] == "OPTIONS":
                # Preflight — return 204 with CORS headers without calling inner app
                from starlette.responses import Response
                response = Response(status_code=204)
                if origin in CORS_ORIGINS:
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Methods"] = "*"
                    response.headers["Access-Control-Allow-Headers"] = "*"
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Max-Age"] = "600"
                await response(scope, receive, send)
                return

            # Non-OPTIONS: forward to inner app, patch headers on the way out
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers_list = message.get("headers", [])
                    if origin:
                        headers_list.append((b"access-control-allow-origin", origin.encode()))
                        headers_list.append((b"access-control-allow-methods", b"*"))
                        headers_list.append((b"access-control-allow-headers", b"*"))
                        headers_list.append((b"access-control-allow-credentials", b"true"))
                    message["headers"] = headers_list
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

# Order: innermost first, outermost last
app.add_middleware(TenantMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSASGIMiddleware)  # outermost — handles OPTIONS before other middleware

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(strategy.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"service": "backend", "status": "ok"}
