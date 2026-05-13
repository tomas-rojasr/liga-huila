from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import not_found_error
from app.dependencies.auth import admin_or_superadmin, get_client_ip, get_current_user
from app.models.lf_team import LfTeam
from app.repositories.audit_repository import create_audit_log
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate

router = APIRouter(prefix="/teams", tags=["Equipos"])


def _team_to_response(team: LfTeam) -> dict:
    return {
        "team_id": team.team_id,
        "club_id": team.club_id,
        "name": team.name,
        "category": team.category,
        "is_active": team.is_active,
        "created_at": team.created_at,
        "club_name": team.club.name if team.club else None,
    }


@router.get("", response_model=List[TeamResponse])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    club_id: UUID = None,
    category: str = None,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    q = db.query(LfTeam).filter(LfTeam.is_deleted == False)
    if club_id:
        q = q.filter(LfTeam.club_id == club_id)
    if category:
        q = q.filter(LfTeam.category == category)
    teams = q.offset(skip).limit(limit).all()
    return [_team_to_response(t) for t in teams]


@router.post("", response_model=TeamResponse)
def create_team(
    body: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    team = LfTeam(**body.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)

    create_audit_log(
        db, action="CREATE", actor_id=current["user"].user_id,
        entity_type="TEAM", entity_id=str(team.team_id),
        description=f"Equipo creado: {team.name}",
        actor_ip=get_client_ip(request),
    )
    return _team_to_response(team)


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    team = db.query(LfTeam).filter(LfTeam.team_id == team_id, LfTeam.is_deleted == False).first()
    if not team:
        raise not_found_error("TEAM")
    return _team_to_response(team)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: UUID,
    body: TeamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    team = db.query(LfTeam).filter(LfTeam.team_id == team_id, LfTeam.is_deleted == False).first()
    if not team:
        raise not_found_error("TEAM")

    old = {"name": team.name, "category": team.category}
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)

    create_audit_log(
        db, action="UPDATE", actor_id=current["user"].user_id,
        entity_type="TEAM", entity_id=str(team_id),
        description=f"Equipo actualizado: {team.name}",
        old_values=old, new_values=body.model_dump(exclude_none=True),
        actor_ip=get_client_ip(request),
    )
    return _team_to_response(team)


@router.delete("/{team_id}")
def delete_team(
    team_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    team = db.query(LfTeam).filter(LfTeam.team_id == team_id, LfTeam.is_deleted == False).first()
    if not team:
        raise not_found_error("TEAM")

    team.is_deleted = True
    team.is_active = False
    db.commit()

    create_audit_log(
        db, action="DELETE", actor_id=current["user"].user_id,
        entity_type="TEAM", entity_id=str(team_id),
        description=f"Equipo eliminado: {team.name}",
        actor_ip=get_client_ip(request),
    )
    return {"message": "Equipo eliminado correctamente"}
