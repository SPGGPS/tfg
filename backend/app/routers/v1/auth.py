"""
Auth - OIDC/Keycloak.
Configuración OIDC, validación de tokens y RBAC.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class TokenValidationRequest(BaseModel):
    token: str


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    roles: Optional[list[str]] = None
    expires_at: Optional[int] = None


@router.get("/oidc/config", response_model=dict)
def oidc_config() -> dict:
    """
    Configuración OIDC para el frontend.
    Proporciona issuer, client_id y otros parámetros necesarios.
    """
    return {
        "issuer": settings.KEYCLOAK_ISSUER,
        "client_id": "tfg-client",  # TODO: Make configurable
        "jwks_uri": settings.KEYCLOAK_JWKS_URI or f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/certs",
        "authorization_endpoint": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/auth",
        "token_endpoint": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token",
        "userinfo_endpoint": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/userinfo",
        "end_session_endpoint": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/logout",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
    }


@router.post("/validate-token", response_model=TokenValidationResponse)
def validate_token(request: TokenValidationRequest) -> TokenValidationResponse:
    """
    Valida un JWT token de Keycloak.
    TODO: Implementar validación real con JWKS.
    Actualmente retorna un placeholder.
    """
    # TODO: Implement actual JWT validation with PyJWT and JWKS
    # For now, return a placeholder response
    return TokenValidationResponse(
        valid=True,
        user_id="placeholder_user",
        roles=["viewer"],  # Default role
        expires_at=None,
    )


# Placeholder dependency for authentication
# TODO: Replace with actual JWT/OIDC validation
async def get_current_user(request: Request) -> str:
    """
    Dependency to extract user from JWT token.
    Currently returns a placeholder.
    TODO: Validate JWT and extract user_id.
    """
    # TODO: Extract and validate JWT from Authorization header
    # For now, return placeholder
    return "authenticated_user"


# Placeholder dependency for role checking
# TODO: Replace with actual JWT/OIDC validation
async def require_role(required_roles: list[str]) -> str:
    """
    Dependency to check if user has required roles.
    Currently returns a placeholder.
    TODO: Extract roles from JWT and validate.
    """
    # TODO: Extract roles from JWT and check against required_roles
    # For now, assume user has all roles (placeholder)
    return "admin_user"  # Placeholder with admin role
