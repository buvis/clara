import secrets

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip CSRF for safe methods
        if request.method in SAFE_METHODS:
            return await call_next(request)

        # Skip CSRF if using Bearer token (API/PAT auth)
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        # Only enforce CSRF when cookie auth is present
        access_cookie = request.cookies.get("access_token")
        if not access_cookie:
            return await call_next(request)

        csrf_cookie = request.cookies.get(CSRF_COOKIE)
        csrf_header = request.headers.get(CSRF_HEADER)

        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return Response(
                content='{"detail":"CSRF token missing or invalid"}',
                status_code=403,
                media_type="application/json",
            )

        return await call_next(request)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose Content-Length exceeds configured limits."""

    async def dispatch(self, request: Request, call_next):
        from clara.config import get_settings

        settings = get_settings()
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                length = int(content_length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
            is_upload = request.url.path.rstrip("/").endswith("/files")
            limit = settings.max_upload_size if is_upload else settings.max_body_size
            if length > limit:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
        return await call_next(request)
