from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, nullable=False)  # api, database, file, agent, manual
    description = Column(Text, nullable=True)

    # Connection details (JSON for flexibility)
    connection_config = Column(JSON, nullable=True)  # URL, credentials, etc.

    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    sync_interval_minutes = Column(Integer, default=60)  # How often to sync
    priority = Column(Integer, default=1)  # For conflict resolution

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assets = relationship("Asset", back_populates="data_source")

    def __repr__(self):
        return f"<DataSource(id='{self.id}', name='{self.name}', type='{self.type}', active={self.is_active})>"