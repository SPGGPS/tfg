"""
Audit logs - consulta de logs de auditoría.
GET con filtros activity_type, user_id, date_range y paginación (máx 100).
Restringido a usuarios con rol admin.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.audit_log import AuditLog

router = APIRouter()


# Placeholder dependency for admin role check
# TODO: Replace with actual JWT/OIDC validation
async def require_admin_role(db: AsyncSession = Depends(get_db)) -> str:
    """
    Dependency to check admin role.
    Currently returns a placeholder user_id.
    TODO: Extract user_id and roles from JWT token.
    """
    # Placeholder - in real implementation, validate JWT and check roles
    db._current_user_id = "admin_user"
    return "admin_user"  # Placeholder user_id


@router.get("", response_model=dict)
async def list_audit_logs(
    activity_type: str = Query(..., description="Tipo de actividad (CREATE, UPDATE, DELETE, etc.)"),
    user_id: str = Query(..., description="ID del usuario"),
    date_from: datetime = Query(..., description="Fecha desde (ISO format)"),
    date_to: datetime = Query(..., description="Fecha hasta (ISO format)"),
    limit: int = Query(100, le=100, description="Límite de resultados (máx 100)"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_role),
) -> dict:
    """
    Lista registros de auditoría con filtros obligatorios.
    Restringido a usuarios con rol admin.
    """
    # Build query with filters
    query = db.query(AuditLog).filter(
        and_(
            AuditLog.activity_type == activity_type,
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= date_from,
            AuditLog.timestamp <= date_to,
        )
    )

    # Get total count
    total = await db.scalar(
        db.query(AuditLog).filter(
            and_(
                AuditLog.activity_type == activity_type,
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= date_from,
                AuditLog.timestamp <= date_to,
            )
        ).count()
    )

    # Get paginated results
    audit_logs = await db.execute(
        query.order_by(desc(AuditLog.timestamp)).limit(limit).offset(offset)
    )
    items = audit_logs.scalars().all()

    return {
        "items": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "activity_type": log.activity_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details,
            }
            for log in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
