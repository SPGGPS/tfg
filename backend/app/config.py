"""Configuración desde variables de entorno."""
import os
from typing import List


def _split_origins(value: str) -> List[str]:
    if not value or not value.strip():
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


class Settings:
    """Configuración de la aplicación."""

    # API
    API_V1_PREFIX: str = "/v1"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

    # CORS (requirement: CORS_ORIGINS)
    CORS_ORIGINS: List[str] = _split_origins(os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"))

    # Keycloak / OIDC (placeholder para integración posterior)
    KEYCLOAK_ISSUER: str = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8080/realms/tfg")
    KEYCLOAK_JWKS_URI: str = os.getenv("KEYCLOAK_JWKS_URI", "")

    # DB - Usar SQLite para testing rápido si no hay PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite://{os.path.abspath('./tfg_test.db')}",  # SQLite para testing rápido
    )


settings = Settings()
