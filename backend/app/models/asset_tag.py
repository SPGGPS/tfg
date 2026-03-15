from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.sql import func

from app.database import Base

asset_tag_table = Table(
    "asset_tags",
    Base.metadata,
    Column("asset_id", String, ForeignKey("assets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now()),
    Column("assigned_by", String, nullable=True),  # User ID who assigned it
)