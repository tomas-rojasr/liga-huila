from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import admin_or_superadmin
from app.repositories.audit_repository import list_audit_logs

router = APIRouter(prefix="/audit", tags=["Auditoría"])


class AuditLogResponse(BaseModel):
    audit_id: UUID
    action: str
    entity_type: str | None
    entity_id: str | None
    description: str | None
    actor_ip: str | None
    created_at: str
    actor_email: str | None = None

    model_config = {"from_attributes": True}


@router.get("")
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    logs = list_audit_logs(
        db, skip=skip, limit=limit,
        action=action, entity_type=entity_type,
        date_from=date_from, date_to=date_to,
    )
    return [
        {
            "audit_id": str(log.audit_id),
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "actor_ip": log.actor_ip,
            "created_at": log.created_at.isoformat(),
            "actor_email": log.actor.email if log.actor else None,
        }
        for log in logs
    ]
