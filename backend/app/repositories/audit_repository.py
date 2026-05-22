from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.lf_audit_log import LfAuditLog


def create_audit_log(
    db: Session,
    action: str,
    actor_id: Optional[UUID] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    description: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    actor_ip: Optional[str] = None,
) -> LfAuditLog:
    log = LfAuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_values=old_values,
        new_values=new_values,
        actor_ip=actor_ip,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    from datetime import datetime, timezone
    query = db.query(LfAuditLog)

    if action:
        query = query.filter(LfAuditLog.action == action.upper())
    if entity_type:
        query = query.filter(LfAuditLog.entity_type == entity_type.upper())
    if date_from:
        dt = datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)
        query = query.filter(LfAuditLog.created_at >= dt)
    if date_to:
        dt = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        query = query.filter(LfAuditLog.created_at <= dt)

    return query.order_by(LfAuditLog.created_at.desc()).offset(skip).limit(limit).all()
