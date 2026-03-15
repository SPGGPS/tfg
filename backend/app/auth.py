"""
Authentication and authorization utilities for Keycloak OIDC integration.
"""
import time
from typing import Dict, Optional

import httpx
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from jose import jwt
from pydantic import BaseModel

from app.config import settings


class UserInfo(BaseModel):
    """User information extracted from JWT token."""
    sub: str
    preferred_username: str
    email: str
    name: str
    roles: list[str] = []
    groups: list[str] = []


class TokenData(BaseModel):
    """Decoded JWT token data."""
    user: UserInfo
    exp: int
    iat: int
    iss: str
    aud: str


# Global cache for JWKS
_jwks_cache: Optional[Dict] = None
_jwks_cache_time: float = 0
JWKS_CACHE_TTL = 3600  # 1 hour


async def get_jwks() -> Dict:
    """
    Fetch and cache JWKS from Keycloak.
    In production, this should be cached properly with Redis or similar.
    """
    global _jwks_cache, _jwks_cache_time

    current_time = time.time()
    if _jwks_cache and (current_time - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache

    # TODO: Configure Keycloak URL in settings
    keycloak_url = getattr(settings, 'KEYCLOAK_URL', 'http://localhost:8080')
    realm = getattr(settings, 'KEYCLOAK_REALM', 'tfg')

    jwks_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/certs"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_cache_time = current_time
            return _jwks_cache
    except Exception as e:
        # Fallback to cached version if available
        if _jwks_cache:
            return _jwks_cache
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )


async def verify_token(token: str) -> TokenData:
    """
    Verify and decode JWT token from Keycloak.
    """
    try:
        # Get the kid (key ID) from the token header
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')

        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token: missing kid")

        # Get JWKS
        jwks = await get_jwks()

        # Find the correct key
        key = None
        for jwk_key in jwks.get('keys', []):
            if jwk_key.get('kid') == kid:
                key = jwk_key
                break

        if not key:
            raise HTTPException(status_code=401, detail="Invalid token: key not found")

        # TODO: Configure Keycloak URL and audience in settings
        keycloak_url = getattr(settings, 'KEYCLOAK_URL', 'http://localhost:8080')
        realm = getattr(settings, 'KEYCLOAK_REALM', 'tfg')
        audience = getattr(settings, 'KEYCLOAK_AUDIENCE', 'tfg-backend')

        # Decode and verify the token
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=audience,
            issuer=f"{keycloak_url}/realms/{realm}"
        )

        # Extract user info
        user_info = UserInfo(
            sub=payload.get('sub', ''),
            preferred_username=payload.get('preferred_username', ''),
            email=payload.get('email', ''),
            name=payload.get('name', ''),
            roles=payload.get('realm_access', {}).get('roles', []),
            groups=payload.get('groups', [])
        )

        return TokenData(
            user=user_info,
            exp=payload.get('exp', 0),
            iat=payload.get('iat', 0),
            iss=payload.get('iss', ''),
            aud=payload.get('aud', '')
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


# Security scheme for OpenAPI docs
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> UserInfo:
    """
    Dependency to get current authenticated user from JWT token.
    For now, returns a placeholder user for development.
    """
    # TODO: Uncomment when Keycloak is properly configured
    # auth_header = await security_scheme(request)
    # if not auth_header:
    #     raise HTTPException(status_code=401, detail="Not authenticated")
    #
    # token_data = await verify_token(auth_header.credentials)
    # return token_data.user

    # Placeholder for development
    return UserInfo(
        sub="dev-user-123",
        preferred_username="developer",
        email="dev@example.com",
        name="Developer User",
        roles=["admin", "editor"],
        groups=["developers"]
    )


def require_role(required_role: str):
    """
    Dependency factory to require specific role.
    Usage: Depends(require_role("admin"))
    """
    async def role_checker(user: UserInfo = Depends(get_current_user)) -> UserInfo:
        if required_role not in user.roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: {required_role} role required"
            )
        return user
    return role_checker


# Convenience dependencies
require_admin = require_role("admin")
require_editor = require_role("editor")
require_viewer = require_role("viewer")