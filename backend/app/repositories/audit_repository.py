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


def list_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(LfAuditLog)
        .order_by(LfAuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
