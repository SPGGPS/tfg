"""
Secure Headers middleware.
Requirement: X-Content-Type-Options, X-Frame-Options, HSTS (when HTTPS), CSP if applicable.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Añade headers de seguridad a todas las respuestas."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # HSTS solo en producción con HTTPS (evitar en localhost)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response
