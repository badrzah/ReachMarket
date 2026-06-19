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

@app.middleware("http")
async def cors_middleware(request, call_next):
    origin = request.headers.get("origin", "")
    if request.method == "OPTIONS":
        from starlette.responses import Response
        response = Response()
    else:
        response = await call_next(request)

    if origin in CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Request-ID"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "600"
    elif origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response

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
