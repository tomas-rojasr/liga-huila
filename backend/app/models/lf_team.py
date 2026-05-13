import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LfTeam(Base):
    __tablename__ = "lf_teams"

    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    club_id = Column(UUID(as_uuid=True), ForeignKey("lf_clubs.club_id", ondelete="SET NULL"), nullable=True)
    name = Column(String(200), nullable=False)
    category = Column(String(20), nullable=False)  # SUB-8|SUB-10|SUB-12|SUB-14|SUB-16|SUB-18|SUB-20|PRIMERA

    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    club = relationship("LfClub", back_populates="teams")
    players = relationship("LfPlayer", back_populates="team")
