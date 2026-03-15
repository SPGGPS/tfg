from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.asset_tag import asset_tag_table


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    color_code = Column(String, nullable=False)  # Hex color code
    description = Column(String, nullable=True)
    origin = Column(String, nullable=False, default="manual")  # "system" or "manual"
    created_by = Column(String, nullable=True)  # User ID who created it
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    assets = relationship("Asset", secondary=asset_tag_table, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, origin={self.origin})>"