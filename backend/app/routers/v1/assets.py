"""
Assets - inventario de activos.
GET /v1/assets con filtros, paginación y historificación.
POST /v1/assets/bulk-tags para asignación masiva de etiquetas.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.auth import UserInfo, get_current_user, require_admin, require_editor
from app.database import get_db
from app.models.asset import Asset
from app.models.asset_tag import asset_tag_table
from app.models.tag import Tag

router = APIRouter()


# Authentication dependencies
async def require_authenticated_user(user: UserInfo = Depends(get_current_user)) -> str:
    """
    Dependency to check authentication and return user ID.
    """
    return user.sub


async def require_admin_role(user: UserInfo = Depends(require_admin)) -> str:
    """
    Dependency to check admin role.
    """
    return user.sub


class BulkTagsRequest(BaseModel):
    asset_ids: List[int]
    tag_ids: List[int]


@router.get("", response_model=dict)
async def list_assets(
    type_filter: Optional[str] = Query(None, description="Filtrar por tipo (server_physical, server_virtual, switch, router, ap)"),
    vendor: Optional[str] = Query(None, description="Filtrar por vendor"),
    source: Optional[str] = Query(None, description="Filtrar por fuente de datos"),
    tag_id: Optional[int] = Query(None, description="Filtrar por tag ID"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre o IP"),
    as_of: Optional[datetime] = Query(None, description="Consultar estado histórico en fecha específica (ISO 8601)"),
    limit: int = Query(50, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_authenticated_user),
) -> dict:
    """
    Lista activos con filtros opcionales y paginación.
    Soporta historificación: usar 'as_of' para consultar estado en fecha específica.
    Incluye información de compliance y etiquetas.
    """
    # Build base query
    query = select(Asset).options(selectinload(Asset.tags))

    # Apply filters
    filters = []
    if type_filter:
        filters.append(Asset.type == type_filter)
    if vendor:
        filters.append(Asset.vendor == vendor)
    if source:
        filters.append(Asset.source == source)
    if search:
        filters.append(
            or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.ips.cast(str).ilike(f"%{search}%")
            )
        )

    if filters:
        query = query.filter(and_(*filters))

    # Apply historification filter
    if as_of:
        # For basic historification, show assets that existed at the specified time
        # This is a simplified version - in production, you'd want proper versioning
        query = query.filter(Asset.created_at <= as_of)

    # Filter by tag if specified
    if tag_id:
        query = query.filter(Asset.tags.any(Tag.id == tag_id))

    # Get total count
    count_query = select(func.count(Asset.id))
    if filters:
        count_query = count_query.filter(and_(*filters))
    if as_of:
        count_query = count_query.filter(Asset.created_at <= as_of)
    if tag_id:
        count_query = count_query.filter(Asset.tags.any(Tag.id == tag_id))

    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Get paginated results
    result = await db.execute(
        query.order_by(desc(Asset.created_at)).limit(limit).offset(offset)
    )
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": asset.id,
                "name": asset.name,
                "type": asset.type,
                "ips": asset.ips,
                "vendor": asset.vendor,
                "source": asset.source,
                "edr_installed": asset.edr_installed,
                "last_backup": asset.last_backup.isoformat() if asset.last_backup else None,
                "monitored": asset.monitored,
                "logs_enabled": asset.logs_enabled,
                "last_sync": asset.last_sync.isoformat() if asset.last_sync else None,
                # Type-specific fields
                "ram_gb": asset.ram_gb,
                "total_disk_gb": asset.total_disk_gb,
                "cpu_count": asset.cpu_count,
                "os": asset.os,
                "model": asset.model,
                "port_count": asset.port_count,
                "firmware_version": asset.firmware_version,
                "max_speed": asset.max_speed,
                "coverage_area": asset.coverage_area,
                "connected_clients": asset.connected_clients,
                "tags": [
                    {
                        "id": tag.id,
                        "name": tag.name,
                        "color_code": tag.color_code,
                        "origin": tag.origin,
                    }
                    for tag in asset.tags
                ],
            }
            for asset in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "as_of": as_of.isoformat() if as_of else None,
        "is_historical": as_of is not None,
    }


@router.post("/bulk-tags", response_model=dict)
async def bulk_assign_tags(
    request: BulkTagsRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Asigna etiquetas a múltiples activos simultáneamente.
    Solo para etiquetas manuales (origin != 'system').
    """
    # Validate that all tags exist and are manual
    tags = await db.execute(
        db.query(Tag).filter(
            and_(
                Tag.id.in_(request.tag_ids),
                Tag.origin != "system"
            )
        )
    )
    found_tags = tags.scalars().all()

    if len(found_tags) != len(request.tag_ids):
        raise HTTPException(
            status_code=400,
            detail="Some tags not found or are system tags"
        )

    # Validate that all assets exist
    assets = await db.execute(
        db.query(Asset).filter(Asset.id.in_(request.asset_ids))
    )
    found_assets = assets.scalars().all()

    if len(found_assets) != len(request.asset_ids):
        raise HTTPException(
            status_code=400,
            detail="Some assets not found"
        )

    # Bulk insert asset-tag associations
    # First, remove existing associations for these assets and tags
    await db.execute(
        asset_tag_table.delete().where(
            and_(
                asset_tag_table.c.asset_id.in_(request.asset_ids),
                asset_tag_table.c.tag_id.in_(request.tag_ids)
            )
        )
    )

    # Insert new associations
    for asset_id in request.asset_ids:
        for tag_id in request.tag_ids:
            await db.execute(
                asset_tag_table.insert().values(
                    asset_id=asset_id,
                    tag_id=tag_id,
                    assigned_by=user_id,
                    assigned_at=datetime.utcnow(),
                )
            )

    await db.commit()

    return {
        "message": f"Successfully assigned {len(request.tag_ids)} tags to {len(request.asset_ids)} assets",
        "asset_count": len(request.asset_ids),
        "tag_count": len(request.tag_ids),
    }


class BulkImportAssetRequest(BaseModel):
    id: str
    name: str
    type: str
    ips: Optional[List[str]] = None
    vendor: Optional[str] = None
    data_source_id: Optional[str] = None
    source: Optional[str] = None
    edr_installed: bool = False
    last_backup: Optional[datetime] = None
    monitored: bool = False
    logs_enabled: bool = False
    ram_gb: Optional[int] = None
    total_disk_gb: Optional[int] = None
    cpu_count: Optional[int] = None
    os: Optional[str] = None
    model: Optional[str] = None
    port_count: Optional[int] = None
    firmware_version: Optional[str] = None
    max_speed: Optional[str] = None
    coverage_area: Optional[str] = None
    connected_clients: Optional[int] = None


class BulkImportRequest(BaseModel):
    assets: List[BulkImportAssetRequest]
    options: Optional[dict] = None


class BulkImportResponse(BaseModel):
    success: bool
    message: str
    imported_count: int
    failed_count: int
    errors: List[dict]
    timestamp: datetime


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_assets(
    request: BulkImportRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> BulkImportResponse:
    """
    Importar múltiples activos desde un JSON de manera segura.
    Valida todos los datos antes de hacer cambios en la base de datos.
    """
    errors = []
    imported_count = 0
    failed_count = 0

    # Validar datos de entrada
    if not request.assets:
        return BulkImportResponse(
            success=False,
            message="No assets provided for import",
            imported_count=0,
            failed_count=0,
            errors=[{"type": "validation", "message": "Assets array is empty"}],
            timestamp=datetime.utcnow(),
        )

    if len(request.assets) > 1000:
        return BulkImportResponse(
            success=False,
            message="Too many assets in single import",
            imported_count=0,
            failed_count=len(request.assets),
            errors=[{"type": "validation", "message": "Maximum 1000 assets per import"}],
            timestamp=datetime.utcnow(),
        )

    # Validar cada asset individualmente
    valid_assets = []
    for i, asset_data in enumerate(request.assets):
        try:
            # Validar campos requeridos
            if not asset_data.id or not asset_data.id.strip():
                errors.append({
                    "index": i,
                    "asset_id": asset_data.id,
                    "type": "validation",
                    "field": "id",
                    "message": "Asset ID is required and cannot be empty"
                })
                failed_count += 1
                continue

            if not asset_data.name or not asset_data.name.strip():
                errors.append({
                    "index": i,
                    "asset_id": asset_data.id,
                    "type": "validation",
                    "field": "name",
                    "message": "Asset name is required and cannot be empty"
                })
                failed_count += 1
                continue

            if not asset_data.type or asset_data.type not in [
                "server_physical", "server_virtual", "switch", "router", "ap"
            ]:
                errors.append({
                    "index": i,
                    "asset_id": asset_data.id,
                    "type": "validation",
                    "field": "type",
                    "message": "Asset type is required and must be one of: server_physical, server_virtual, switch, router, ap"
                })
                failed_count += 1
                continue

            # Verificar si el asset ya existe
            existing = await db.execute(select(Asset).where(Asset.id == asset_data.id))
            if existing.scalar_one_or_none():
                errors.append({
                    "index": i,
                    "asset_id": asset_data.id,
                    "type": "conflict",
                    "message": "Asset with this ID already exists"
                })
                failed_count += 1
                continue

            # Validar data_source_id si se proporciona
            if asset_data.data_source_id:
                from app.models.data_source import DataSource
                ds_result = await db.execute(select(DataSource).where(DataSource.id == asset_data.data_source_id))
                if not ds_result.scalar_one_or_none():
                    errors.append({
                        "index": i,
                        "asset_id": asset_data.id,
                        "type": "validation",
                        "field": "data_source_id",
                        "message": f"Data source '{asset_data.data_source_id}' does not exist"
                    })
                    failed_count += 1
                    continue

            valid_assets.append(asset_data)

        except Exception as e:
            errors.append({
                "index": i,
                "asset_id": getattr(asset_data, 'id', 'unknown'),
                "type": "validation",
                "message": f"Unexpected validation error: {str(e)}"
            })
            failed_count += 1

    # Si hay errores de validación, no proceder con la importación
    if errors:
        return BulkImportResponse(
            success=False,
            message=f"Validation failed for {len(errors)} assets",
            imported_count=0,
            failed_count=failed_count,
            errors=errors,
            timestamp=datetime.utcnow(),
        )

    # Importar assets válidos en una transacción
    try:
        for asset_data in valid_assets:
            asset = Asset(
                id=asset_data.id,
                name=asset_data.name,
                type=asset_data.type,
                ips=asset_data.ips,
                vendor=asset_data.vendor,
                data_source_id=asset_data.data_source_id,
                source=asset_data.source,
                edr_installed=asset_data.edr_installed,
                last_backup=asset_data.last_backup,
                monitored=asset_data.monitored,
                logs_enabled=asset_data.logs_enabled,
                ram_gb=asset_data.ram_gb,
                total_disk_gb=asset_data.total_disk_gb,
                cpu_count=asset_data.cpu_count,
                os=asset_data.os,
                model=asset_data.model,
                port_count=asset_data.port_count,
                firmware_version=asset_data.firmware_version,
                max_speed=asset_data.max_speed,
                coverage_area=asset_data.coverage_area,
                connected_clients=asset_data.connected_clients,
                last_sync=datetime.utcnow(),
            )
            db.add(asset)
            imported_count += 1

        await db.commit()

        return BulkImportResponse(
            success=True,
            message=f"Successfully imported {imported_count} assets",
            imported_count=imported_count,
            failed_count=0,
            errors=[],
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        await db.rollback()
        return BulkImportResponse(
            success=False,
            message=f"Import failed due to database error: {str(e)}",
            imported_count=0,
            failed_count=len(valid_assets),
            errors=[{
                "type": "database",
                "message": f"Database error during import: {str(e)}"
            }],
            timestamp=datetime.utcnow(),
        )
