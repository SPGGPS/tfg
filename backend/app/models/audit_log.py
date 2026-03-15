from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String
from sqlalchemy.sql import func

from app.database import Base


class AuditActivityType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    TAG_ASSIGN = "TAG_ASSIGN"
    LOGIN = "LOGIN"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    activity_type = Column(String, nullable=False, index=True)  # Using String instead of Enum for flexibility
    resource_type = Column(String, nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
    details = Column(JSON, nullable=False, default=dict)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, activity_type={self.activity_type})>"