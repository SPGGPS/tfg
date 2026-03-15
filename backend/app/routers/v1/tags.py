"""
Tags - gestión de etiquetas.
CRUD completo con protección de etiquetas de sistema.
Solo admin puede crear, editar y borrar etiquetas manuales.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import UserInfo, get_current_user, require_admin
from app.database import get_db
from app.models.tag import Tag

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


class TagCreateRequest(BaseModel):
    name: str
    color_code: str
    description: Optional[str] = None


class TagUpdateRequest(BaseModel):
    name: Optional[str] = None
    color_code: Optional[str] = None
    description: Optional[str] = None


@router.get("", response_model=dict)
async def list_tags(
    origin: Optional[str] = Query(None, description="Filtrar por origen (manual, system)"),
    search: Optional[str] = Query(None, description="Búsqueda por nombre"),
    limit: int = Query(50, le=100, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_authenticated_user),
) -> dict:
    """
    Lista etiquetas con filtros opcionales.
    Incluye estadísticas de uso (número de activos asociados).
    """
    # Build query
    query = db.query(Tag)

    # Apply filters
    filters = []
    if origin:
        filters.append(Tag.origin == origin)
    if search:
        filters.append(Tag.name.ilike(f"%{search}%"))

    if filters:
        query = query.filter(and_(*filters))

    # Get total count
    total = await db.scalar(select(func.count()).select_from(Tag))

    # Get paginated results
    tags = await db.execute(
        query.order_by(desc(Tag.created_at)).limit(limit).offset(offset)
    )
    items = tags.scalars().all()

    # For each tag, get the count of associated assets
    # This is a simplified version - in production, you'd want to optimize this
    result_items = []
    for tag in items:
        # Count associated assets
        asset_count = await db.scalar(
            db.query(Tag).filter(Tag.id == tag.id).first().assets.count()
        ) if hasattr(tag, 'assets') else 0

        result_items.append({
            "id": tag.id,
            "name": tag.name,
            "color_code": tag.color_code,
            "description": tag.description,
            "origin": tag.origin,
            "created_by": tag.created_by,
            "created_at": tag.created_at.isoformat(),
            "updated_at": tag.updated_at.isoformat() if tag.updated_at else None,
            "asset_count": asset_count,
        })

    return {
        "items": result_items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=dict)
async def create_tag(
    request: TagCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Crea una nueva etiqueta manual.
    Solo para usuarios con rol admin.
    """
    # Check if tag name already exists
    existing = await db.scalar(
        db.query(Tag).filter(Tag.name == request.name).count()
    )
    if existing > 0:
        raise HTTPException(
            status_code=400,
            detail="Tag name already exists"
        )

    # Create new tag
    tag = Tag(
        name=request.name,
        color_code=request.color_code,
        description=request.description,
        origin="manual",
        created_by=user_id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    return {
        "id": tag.id,
        "name": tag.name,
        "color_code": tag.color_code,
        "description": tag.description,
        "origin": tag.origin,
        "created_by": tag.created_by,
        "created_at": tag.created_at.isoformat(),
        "asset_count": 0,
    }


@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: int,
    request: TagUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Actualiza una etiqueta manual.
    Solo para usuarios con rol admin.
    No se pueden modificar etiquetas de sistema.
    """
    # Get the tag
    tag = await db.scalar(
        db.query(Tag).filter(Tag.id == tag_id)
    )

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if it's a system tag
    if tag.origin == "system":
        raise HTTPException(
            status_code=400,
            detail="Cannot modify system tags"
        )

    # Check name uniqueness if name is being changed
    if request.name and request.name != tag.name:
        existing = await db.scalar(
            db.query(Tag).filter(
                and_(Tag.name == request.name, Tag.id != tag_id)
            ).count()
        )
        if existing > 0:
            raise HTTPException(
                status_code=400,
                detail="Tag name already exists"
            )

    # Update fields
    if request.name is not None:
        tag.name = request.name
    if request.color_code is not None:
        tag.color_code = request.color_code
    if request.description is not None:
        tag.description = request.description

    tag.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(tag)

    # Get asset count
    asset_count = await db.scalar(
        db.query(Tag).filter(Tag.id == tag.id).first().assets.count()
    ) if hasattr(tag, 'assets') else 0

    return {
        "id": tag.id,
        "name": tag.name,
        "color_code": tag.color_code,
        "description": tag.description,
        "origin": tag.origin,
        "created_by": tag.created_by,
        "created_at": tag.created_at.isoformat(),
        "updated_at": tag.updated_at.isoformat() if tag.updated_at else None,
        "asset_count": asset_count,
    }


@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_admin_role),
) -> dict:
    """
    Elimina una etiqueta manual.
    Solo para usuarios con rol admin.
    No se pueden eliminar etiquetas de sistema.
    """
    # Get the tag
    tag = await db.scalar(
        db.query(Tag).filter(Tag.id == tag_id)
    )

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if it's a system tag
    if tag.origin == "system":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete system tags"
        )

    # Get asset count before deletion
    asset_count = await db.scalar(
        db.query(Tag).filter(Tag.id == tag.id).first().assets.count()
    ) if hasattr(tag, 'assets') else 0

    # Delete the tag (CASCADE will handle asset_tag associations)
    await db.delete(tag)
    await db.commit()

    return {
        "message": f"Tag '{tag.name}' deleted successfully",
        "asset_count": asset_count,
    }
