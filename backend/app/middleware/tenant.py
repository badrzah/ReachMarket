from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from backend.app.config import settings
import uuid

# Paths that are either public or handle their own auth (e.g. SSE with query-param JWT).
AUTH_ROUTES = {"/api/v1/auth/login", "/api/v1/auth/register", "/health"}
SELF_AUTH_PREFIXES = ("/api/v1/strategy/generate/stream",)

# Demo user for when no token is provided
DEMO_COMPANY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if (
            path in AUTH_ROUTES
            or request.method == "OPTIONS"
            or not path.startswith("/api/v1/")
            or path.startswith(SELF_AUTH_PREFIXES)
        ):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            try:
                payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
                company_id = payload.get("company_id")
                if company_id:
                    request.state.company_id = company_id
                    request.state.user_id = payload.get("sub")
                    request.state.role = payload.get("role", "member")
                    return await call_next(request)
            except JWTError:
                pass

        # Demo mode: no valid token — use demo user
        request.state.company_id = str(DEMO_COMPANY_ID)
        request.state.user_id = str(DEMO_USER_ID)
        request.state.role = "owner"

        return await call_next(request)
