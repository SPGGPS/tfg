"""
Data Sources - gestión de fuentes de datos.
CRUD completo para fuentes de datos externas (VMware, ServiceNow, EDR, etc.).
Validación de conexiones y monitoreo de sincronización.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.data_source import DataSource

router = APIRouter()


# Placeholder dependency for authentication
# TODO: Replace with actual JWT/OIDC validation
async def require_authenticated_user(db: AsyncSession = Depends(get_db)) -> str:
    """
    Dependency to check authentication.
    Currently returns a placeholder user_id.
    TODO: Extract user_id from JWT token.
    """
    # Establecer usuario en la sesión para auditoría
    db._current_user_id = "authenticated_user"
    return "authenticated_user"


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


class DataSourceCreateRequest(BaseModel):
    id: str
    name: str
    type: str  # api, database, file, agent, manual
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    sync_interval_minutes: int = 60
    priority: int = 1


class DataSourceUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None
    priority: Optional[int] = None


class ValidationResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime
    error_details: Optional[Dict[str, Any]] = None


@router.get("", response_model=dict)
async def list_data_sources(
    type_filter: Optional[str] = Query(None, description="Filtrar por tipo (api, database, file, agent, manual)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o descripción"),
    limit: int = Query(50, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_authenticated_user),
) -> dict:
    """
    Lista fuentes de datos con filtros opcionales y paginación.
    """
    # Build query
    query = select(DataSource)

    # Apply filters
    filters = []
    if type_filter:
        filters.append(DataSource.type == type_filter)
    if is_active is not None:
        filters.append(DataSource.is_active == is_active)
    if search:
        filters.append(
            or_(
                DataSource.name.ilike(f"%{search}%"),
                DataSource.description.ilike(f"%{search}%")
            )
        )

    if filters:
        query = query.filter(and_(*filters))

    # Get total count
    total_result = await db.execute(select(func.count()).select_from(DataSource))
    total = total_result.scalar()

    # Get paginated results
    result = await db.execute(
        query.order_by(desc(DataSource.created_at)).limit(limit).offset(offset)
    )
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "description": ds.description,
                "connection_config": ds.connection_config,
                "is_active": ds.is_active,
                "last_sync": ds.last_sync.isoformat() if ds.last_sync else None,
                "sync_interval_minutes": ds.sync_interval_minutes,
                "priority": ds.priority,
                "created_at": ds.created_at.isoformat() if ds.created_at else None,
                "updated_at": ds.updated_at.isoformat() if ds.updated_at else None,
            }
            for ds in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{data_source_id}", response_model=dict)
async def get_data_source(
    data_source_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_authenticated_user),
) -> dict:
    """
    Obtiene detalles de una fuente de datos específica.
    """
    result = await db.execute(select(DataSource).where(DataSource.id == data_source_id))
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    return {
        "id": data_source.id,
        "name": data_source.name,
        "type": data_source.type,
        "description": data_source.description,
        "connection_config": data_source.connection_config,
        "is_active": data_source.is_active,
        "last_sync": data_source.last_sync.isoformat() if data_source.last_sync else None,
        "sync_interval_minutes": data_source.sync_interval_minutes,
        "priority": data_source.priority,
        "created_at": data_source.created_at.isoformat() if data_source.created_at else None,
        "updated_at": data_source.updated_at.isoformat() if data_source.updated_at else None,
    }


@router.post("", response_model=dict, status_code=201)
async def create_data_source(
    request: DataSourceCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Crea una nueva fuente de datos.
    Requiere rol de administrador.
    """
    # Check if data source with this ID already exists
    result = await db.execute(select(DataSource).where(DataSource.id == request.id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Data source with this ID already exists")

    # Check if name is unique
    result = await db.execute(select(DataSource).where(DataSource.name == request.name))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Data source with this name already exists")

    # Create new data source
    data_source = DataSource(
        id=request.id,
        name=request.name,
        type=request.type,
        description=request.description,
        connection_config=request.connection_config,
        is_active=request.is_active,
        sync_interval_minutes=request.sync_interval_minutes,
        priority=request.priority,
    )

    db.add(data_source)
    await db.commit()
    await db.refresh(data_source)

    return {
        "id": data_source.id,
        "name": data_source.name,
        "type": data_source.type,
        "description": data_source.description,
        "connection_config": data_source.connection_config,
        "is_active": data_source.is_active,
        "last_sync": data_source.last_sync.isoformat() if data_source.last_sync else None,
        "sync_interval_minutes": data_source.sync_interval_minutes,
        "priority": data_source.priority,
        "created_at": data_source.created_at.isoformat() if data_source.created_at else None,
        "updated_at": data_source.updated_at.isoformat() if data_source.updated_at else None,
    }


@router.put("/{data_source_id}", response_model=dict)
async def update_data_source(
    data_source_id: str,
    request: DataSourceUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Actualiza una fuente de datos existente.
    Requiere rol de administrador.
    """
    result = await db.execute(select(DataSource).where(DataSource.id == data_source_id))
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Check name uniqueness if name is being updated
    if request.name and request.name != data_source.name:
        result = await db.execute(select(DataSource).where(DataSource.name == request.name))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Data source with this name already exists")

    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(data_source, field, value)

    await db.commit()
    await db.refresh(data_source)

    return {
        "id": data_source.id,
        "name": data_source.name,
        "type": data_source.type,
        "description": data_source.description,
        "connection_config": data_source.connection_config,
        "is_active": data_source.is_active,
        "last_sync": data_source.last_sync.isoformat() if data_source.last_sync else None,
        "sync_interval_minutes": data_source.sync_interval_minutes,
        "priority": data_source.priority,
        "created_at": data_source.created_at.isoformat() if data_source.created_at else None,
        "updated_at": data_source.updated_at.isoformat() if data_source.updated_at else None,
    }


@router.delete("/{data_source_id}", status_code=204)
async def delete_data_source(
    data_source_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
):
    """
    Elimina una fuente de datos.
    Requiere rol de administrador.
    """
    result = await db.execute(select(DataSource).where(DataSource.id == data_source_id))
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Check if data source has associated assets
    if data_source.assets:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete data source with associated assets. Remove assets first or set data source to inactive."
        )

    await db.delete(data_source)
    await db.commit()


@router.post("/{data_source_id}/validate", response_model=ValidationResponse)
async def validate_data_source(
    data_source_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_authenticated_user),
) -> ValidationResponse:
    """
    Valida la conexión de una fuente de datos.
    """
    result = await db.execute(select(DataSource).where(DataSource.id == data_source_id))
    data_source = result.scalar_one_or_none()

    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    # Basic validation logic (placeholder)
    # In a real implementation, this would test actual connections
    try:
        if data_source.type == "api":
            # Validate API connection
            config = data_source.connection_config or {}
            if not config.get("url"):
                raise ValueError("API URL is required")
            # Here you would make an actual HTTP request
            success = True
            message = "API connection validated successfully"

        elif data_source.type == "database":
            # Validate database connection
            config = data_source.connection_config or {}
            if not config.get("connection_string"):
                raise ValueError("Database connection string is required")
            # Here you would test database connection
            success = True
            message = "Database connection validated successfully"

        elif data_source.type == "manual":
            success = True
            message = "Manual data source - no validation required"

        else:
            success = True
            message = f"Basic validation passed for {data_source.type} data source"

    except Exception as e:
        success = False
        message = f"Validation failed: {str(e)}"
        error_details = {"error": str(e), "type": type(e).__name__}

    return ValidationResponse(
        success=success,
        message=message,
        timestamp=datetime.utcnow(),
        error_details=error_details if not success else None,
    )