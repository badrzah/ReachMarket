from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from backend.app.config import settings

# Paths that are either public or handle their own auth (e.g. SSE with query-param JWT).
AUTH_ROUTES = {"/api/v1/auth/login", "/api/v1/auth/register", "/health"}
SELF_AUTH_PREFIXES = ("/api/v1/strategy/generate/stream",)

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
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

        token = auth_header.removeprefix("Bearer ")
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            company_id: str = payload.get("company_id")
            if not company_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        request.state.company_id = company_id
        request.state.user_id = payload.get("sub")
        request.state.role = payload.get("role", "member")

        return await call_next(request)
