from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.lf_club import LfClub
from app.models.lf_player import LfPlayer
from app.models.lf_team import LfTeam
from app.models.lf_user import LfUser

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    total_clubs = db.query(LfClub).filter(LfClub.is_deleted == False).count()
    active_clubs = db.query(LfClub).filter(LfClub.is_deleted == False, LfClub.is_active == True).count()
    total_teams = db.query(LfTeam).filter(LfTeam.is_deleted == False).count()
    total_players = db.query(LfPlayer).filter(LfPlayer.is_deleted == False).count()
    total_users = db.query(LfUser).filter(LfUser.is_deleted == False).count()

    players_by_category = (
        db.query(LfPlayer.category, db.query(LfPlayer).filter(LfPlayer.is_deleted == False).count())
        .filter(LfPlayer.is_deleted == False)
        .group_by(LfPlayer.category)
        .all()
    )

    from sqlalchemy import func
    category_counts = (
        db.query(LfPlayer.category, func.count(LfPlayer.player_id))
        .filter(LfPlayer.is_deleted == False)
        .group_by(LfPlayer.category)
        .all()
    )

    return {
        "total_clubs": total_clubs,
        "active_clubs": active_clubs,
        "total_teams": total_teams,
        "total_players": total_players,
        "total_users": total_users,
        "players_by_category": [{"category": cat, "count": cnt} for cat, cnt in category_counts],
    }
