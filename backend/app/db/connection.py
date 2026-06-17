import asyncpg
from fastapi import Request
from backend.app.config import settings

_pool: asyncpg.Pool | None = None

async def init_pool() -> None:
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )

async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized — call init_pool() first")
    return _pool

async def get_db_tenant(request: Request):
    """Get a DB connection with RLS enforced (for tenant-scoped operations)."""
    assert _pool is not None, "Database pool not initialized"
    async with _pool.acquire() as conn:
        company_id = getattr(request.state, "company_id", None)
        if company_id:
            await conn.execute(
                "SELECT set_config('app.current_company_id', $1, FALSE)", company_id
            )
        yield conn

async def get_db_auth(request: Request):
    """Get a DB connection without RLS isolation (for login/register).
    
    Doesn't set company context, so the RLS policy on users allows
    email-based lookups across all tenants. This is safe because the
    user still needs valid credentials to authenticate.
    """
    assert _pool is not None, "Database pool not initialized"
    async with _pool.acquire() as conn:
        yield conn
