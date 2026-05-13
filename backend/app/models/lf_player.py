import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class LfPlayer(Base):
    __tablename__ = "lf_players"

    player_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("lf_teams.team_id", ondelete="SET NULL"), nullable=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    category = Column(String(20), nullable=False)  # calculado automáticamente por edad

    document_type = Column(String(20), nullable=False, default="CC")  # CC|TI|CE|PASAPORTE
    document_number = Column(String(50), nullable=False, unique=True, index=True)
    nationality = Column(String(100), nullable=False, default="Colombiana")
    position = Column(String(50), nullable=True)  # Portero|Defensa|Mediocampista|Delantero
    photo_url = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, default="ACTIVO")  # ACTIVO|INACTIVO|SUSPENDIDO|TRANSFERIDO

    is_deleted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    team = relationship("LfTeam", back_populates="players")
