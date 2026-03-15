"""
TFG Backend - FastAPI.
OpenAPI 3.1, CORS configurable, Secure Headers, /v1/healthz.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.middleware.secure_headers import SecureHeadersMiddleware
from app.routers import v1


app = FastAPI(
    title="TFG API",
    description="CMDB - Inventario, etiquetas y auditoría",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Crear tablas al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    from sqlalchemy import create_engine
    # Crear engine síncrono para crear tablas
    db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite:///")
    sync_engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(bind=sync_engine)
    sync_engine.dispose()


# CORS (requirement: configurable via CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Secure Headers (requirement: X-Content-Type-Options, X-Frame-Options, etc.)
app.add_middleware(SecureHeadersMiddleware)

# Routers (todos bajo /v1, incl. /v1/healthz)
app.include_router(v1.router, prefix=settings.API_V1_PREFIX)
