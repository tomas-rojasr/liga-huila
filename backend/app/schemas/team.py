from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

VALID_CATEGORIES = ("SUB-8", "SUB-10", "SUB-12", "SUB-14", "SUB-16", "SUB-18", "SUB-20", "PRIMERA")


class TeamCreate(BaseModel):
    club_id: Optional[UUID] = None
    name: str
    category: str

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Categoría inválida. Válidas: {VALID_CATEGORIES}")
        return v


class TeamUpdate(BaseModel):
    club_id: Optional[UUID] = None
    name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v and v not in VALID_CATEGORIES:
            raise ValueError(f"Categoría inválida. Válidas: {VALID_CATEGORIES}")
        return v


class TeamResponse(BaseModel):
    team_id: UUID
    club_id: Optional[UUID]
    name: str
    category: str
    is_active: bool
    created_at: datetime
    club_name: Optional[str] = None

    model_config = {"from_attributes": True}
