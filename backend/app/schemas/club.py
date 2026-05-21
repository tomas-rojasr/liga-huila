from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class ClubCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre del club no puede estar vacío")
        return v
    code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None


class ClubUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ClubResponse(BaseModel):
    club_id: UUID
    name: str
    code: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    logo_url: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
