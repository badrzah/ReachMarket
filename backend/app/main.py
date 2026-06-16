from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.app.db.connection import init_pool, close_pool, get_pool
from backend.app.middleware.tenant import TenantMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.api import auth, chat, strategy, content, knowledge
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CORSHeaderMiddleware(BaseHTTPMiddleware):
    """Add CORS headers manually since Railway's proxy strips the standard ones."""
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin", "")
        response: Response = await call_next(request)
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        if request.method == "OPTIONS":
            response.status_code = 204
        return response

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

# Custom CORS middleware (outermost, runs first)
app.add_middleware(CORSHeaderMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(strategy.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"service": "backend", "status": "ok"}
