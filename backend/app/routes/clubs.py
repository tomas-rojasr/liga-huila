from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import api_error, not_found_error
from app.dependencies.auth import admin_or_superadmin, get_client_ip, get_current_user
from app.models.lf_club import LfClub
from app.repositories.audit_repository import create_audit_log
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate

router = APIRouter(prefix="/clubs", tags=["Clubes"])


@router.get("", response_model=List[ClubResponse])
def list_clubs(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    q = db.query(LfClub).filter(LfClub.is_deleted == False)
    if active_only:
        q = q.filter(LfClub.is_active == True)
    return q.offset(skip).limit(limit).all()


@router.post("", response_model=ClubResponse)
def create_club(
    body: ClubCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    if db.query(LfClub).filter(LfClub.code == body.code, LfClub.is_deleted == False).first():
        raise api_error("CLUB_CODE_ALREADY_EXISTS")

    club = LfClub(**body.model_dump())
    db.add(club)
    db.commit()
    db.refresh(club)

    create_audit_log(
        db, action="CREATE", actor_id=current["user"].user_id,
        entity_type="CLUB", entity_id=str(club.club_id),
        description=f"Club creado: {club.name}",
        actor_ip=get_client_ip(request),
    )
    return club


@router.get("/{club_id}", response_model=ClubResponse)
def get_club(
    club_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    club = db.query(LfClub).filter(LfClub.club_id == club_id, LfClub.is_deleted == False).first()
    if not club:
        raise not_found_error("CLUB")
    return club


@router.put("/{club_id}", response_model=ClubResponse)
def update_club(
    club_id: UUID,
    body: ClubUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    club = db.query(LfClub).filter(LfClub.club_id == club_id, LfClub.is_deleted == False).first()
    if not club:
        raise not_found_error("CLUB")

    old = {"name": club.name, "is_active": club.is_active}
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(club, field, value)
    db.commit()
    db.refresh(club)

    create_audit_log(
        db, action="UPDATE", actor_id=current["user"].user_id,
        entity_type="CLUB", entity_id=str(club_id),
        description=f"Club actualizado: {club.name}",
        old_values=old, new_values=body.model_dump(exclude_none=True),
        actor_ip=get_client_ip(request),
    )
    return club


@router.delete("/{club_id}")
def delete_club(
    club_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    club = db.query(LfClub).filter(LfClub.club_id == club_id, LfClub.is_deleted == False).first()
    if not club:
        raise not_found_error("CLUB")

    club.is_deleted = True
    club.is_active = False
    db.commit()

    create_audit_log(
        db, action="DELETE", actor_id=current["user"].user_id,
        entity_type="CLUB", entity_id=str(club_id),
        description=f"Club eliminado: {club.name}",
        actor_ip=get_client_ip(request),
    )
    return {"message": "Club eliminado correctamente"}
