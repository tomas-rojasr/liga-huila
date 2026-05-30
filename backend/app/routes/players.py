from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, outerjoin
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import api_error, not_found_error
from app.dependencies.auth import admin_or_superadmin, get_client_ip, get_current_user
from app.models.lf_player import LfPlayer
from app.models.lf_team import LfTeam
from app.repositories.audit_repository import create_audit_log
from app.schemas.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.services.category_service import calculate_category

router = APIRouter(prefix="/players", tags=["Jugadores"])


def _player_to_response(player: LfPlayer) -> dict:
    return {
        "player_id": player.player_id,
        "team_id": player.team_id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "birth_date": player.birth_date,
        "category": player.category,
        "document_type": player.document_type,
        "document_number": player.document_number,
        "nationality": player.nationality,
        "position": player.position,
        "photo_url": player.photo_url,
        "status": player.status,
        "created_at": player.created_at,
        "team_name": player.team.name if player.team else None,
    }


@router.get("", response_model=List[PlayerResponse])
def list_players(
    team_id: UUID = None,
    category: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    q = (
        db.query(LfPlayer, LfTeam.name.label("team_name"))
        .outerjoin(LfTeam, LfPlayer.team_id == LfTeam.team_id)
        .filter(LfPlayer.is_deleted == False)
    )
    if team_id:
        q = q.filter(LfPlayer.team_id == team_id)
    if category:
        q = q.filter(LfPlayer.category == category)
    if status:
        q = q.filter(LfPlayer.status == status)

    rows = q.order_by(LfPlayer.created_at.desc()).all()

    return [
        {
            "player_id": p.player_id,
            "team_id": p.team_id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "birth_date": p.birth_date,
            "category": p.category,
            "document_type": p.document_type,
            "document_number": p.document_number,
            "nationality": p.nationality,
            "position": p.position,
            "photo_url": p.photo_url,
            "status": p.status,
            "created_at": p.created_at,
            "team_name": team_name,
        }
        for p, team_name in rows
    ]


@router.post("", response_model=PlayerResponse)
def create_player(
    body: PlayerCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    if db.query(LfPlayer).filter(
        LfPlayer.document_number == body.document_number, LfPlayer.is_deleted == False
    ).first():
        raise api_error("DOCUMENT_NUMBER_ALREADY_EXISTS")

    category = calculate_category(body.birth_date)
    data = body.model_dump()
    data["category"] = category

    player = LfPlayer(**data)
    db.add(player)
    db.commit()
    db.refresh(player)

    create_audit_log(
        db, action="CREATE", actor_id=current["user"].user_id,
        entity_type="PLAYER", entity_id=str(player.player_id),
        description=f"Patinador creado: {player.first_name} {player.last_name}",
        actor_ip=get_client_ip(request),
    )
    return _player_to_response(player)


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    player = db.query(LfPlayer).filter(LfPlayer.player_id == player_id, LfPlayer.is_deleted == False).first()
    if not player:
        raise not_found_error("PLAYER")
    return _player_to_response(player)


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: UUID,
    body: PlayerUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    player = db.query(LfPlayer).filter(LfPlayer.player_id == player_id, LfPlayer.is_deleted == False).first()
    if not player:
        raise not_found_error("PLAYER")

    old = {"status": player.status, "team_id": str(player.team_id) if player.team_id else None}
    data = body.model_dump(exclude_unset=True)

    if "birth_date" in data:
        data["category"] = calculate_category(data["birth_date"])

    for field, value in data.items():
        setattr(player, field, value)
    db.commit()
    db.refresh(player)

    audit_data = body.model_dump(mode="json", exclude_unset=True)

    create_audit_log(
        db, action="UPDATE", actor_id=current["user"].user_id,
        entity_type="PLAYER", entity_id=str(player_id),
        description=f"Patinador actualizado: {player.first_name} {player.last_name}",
        old_values=old, new_values=audit_data,
        actor_ip=get_client_ip(request),
    )
    return _player_to_response(player)


@router.delete("/{player_id}")
def delete_player(
    player_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    player = db.query(LfPlayer).filter(LfPlayer.player_id == player_id, LfPlayer.is_deleted == False).first()
    if not player:
        raise not_found_error("PLAYER")

    player.is_deleted = True
    db.commit()

    create_audit_log(
        db, action="DELETE", actor_id=current["user"].user_id,
        entity_type="PLAYER", entity_id=str(player_id),
        description=f"Patinador eliminado: {player.first_name} {player.last_name}",
        actor_ip=get_client_ip(request),
    )
    return {"message": "Jugador eliminado correctamente"}
