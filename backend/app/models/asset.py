from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.asset_tag import asset_tag_table


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # server_physical, server_virtual, switch, router, ap

    # Basic fields
    ips = Column(JSON, nullable=True)  # Array of IP addresses
    vendor = Column(String, nullable=True)
    data_source_id = Column(String, ForeignKey("data_sources.id"), nullable=True)

    # Legacy source field (for backward compatibility)
    source = Column(String, nullable=True)  # VMware, Veeam, Monica, ServiceNow, EDR, Monitorización

    # Compliance fields
    edr_installed = Column(Boolean, default=False)
    last_backup = Column(DateTime(timezone=True), nullable=True)
    monitored = Column(Boolean, default=False)
    logs_enabled = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True), default=func.now())

    # Type-specific fields (nullable, used based on type)
    # Server fields
    ram_gb = Column(Integer, nullable=True)
    total_disk_gb = Column(Integer, nullable=True)
    cpu_count = Column(Integer, nullable=True)
    os = Column(String, nullable=True)

    # Network device fields
    model = Column(String, nullable=True)
    port_count = Column(Integer, nullable=True)
    firmware_version = Column(String, nullable=True)
    max_speed = Column(String, nullable=True)  # For switches
    coverage_area = Column(String, nullable=True)  # For APs
    connected_clients = Column(Integer, nullable=True)  # For APs

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tags = relationship("Tag", secondary=asset_tag_table, back_populates="assets")
    data_source = relationship("DataSource", back_populates="assets")

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, type={self.type})>"