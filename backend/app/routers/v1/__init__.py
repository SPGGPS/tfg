# v1 API
from fastapi import APIRouter
from app.routers import health
from app.routers.v1 import assets, audit_logs, auth, data_sources, tags

router = APIRouter()

router.include_router(health.router, prefix="", tags=["health"])
router.include_router(assets.router, prefix="/assets", tags=["assets"])
router.include_router(tags.router, prefix="/tags", tags=["tags"])
router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
