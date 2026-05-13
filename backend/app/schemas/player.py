from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

VALID_STATUSES = ("ACTIVO", "INACTIVO", "SUSPENDIDO", "TRANSFERIDO")
VALID_POSITIONS = ("Portero", "Defensa", "Mediocampista", "Delantero")
VALID_DOC_TYPES = ("CC", "TI", "CE", "PASAPORTE")


class PlayerCreate(BaseModel):
    team_id: Optional[UUID] = None
    first_name: str
    last_name: str
    birth_date: date
    document_type: str = "CC"
    document_number: str
    nationality: str = "Colombiana"
    position: Optional[str] = None
    photo_url: Optional[str] = None
    status: str = "ACTIVO"

    @field_validator("document_type")
    @classmethod
    def validate_doc_type(cls, v):
        if v not in VALID_DOC_TYPES:
            raise ValueError(f"Tipo de documento inválido. Válidos: {VALID_DOC_TYPES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in VALID_STATUSES:
            raise ValueError(f"Estado inválido. Válidos: {VALID_STATUSES}")
        return v


class PlayerUpdate(BaseModel):
    team_id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    photo_url: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in VALID_STATUSES:
            raise ValueError(f"Estado inválido. Válidos: {VALID_STATUSES}")
        return v


class PlayerResponse(BaseModel):
    player_id: UUID
    team_id: Optional[UUID]
    first_name: str
    last_name: str
    birth_date: date
    category: str
    document_type: str
    document_number: str
    nationality: str
    position: Optional[str]
    photo_url: Optional[str]
    status: str
    created_at: datetime
    team_name: Optional[str] = None

    model_config = {"from_attributes": True}
