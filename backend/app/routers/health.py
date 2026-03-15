"""
Health check para liveness/readiness probes (Kubernetes).
Requirement: GET /v1/healthz → 200 { "status": "ok" }
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", response_model=dict)
def healthz() -> dict:
    """Liveness/readiness probe."""
    return {"status": "ok"}
