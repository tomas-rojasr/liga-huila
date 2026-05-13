import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LfAuditLog(Base):
    __tablename__ = "lf_audit_log"

    audit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("lf_users.user_id", ondelete="SET NULL"), nullable=True)

    action = Column(String(50), nullable=False)         # CREATE|UPDATE|DELETE|LOGIN|LOGOUT
    entity_type = Column(String(50), nullable=True)     # USER|CLUB|TEAM|PLAYER
    entity_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    actor_ip = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actor = relationship("LfUser", back_populates="audit_logs")
