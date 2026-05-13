from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import api_error, not_found_error
from app.core.security import get_password_hash
from app.dependencies.auth import admin_or_superadmin, get_client_ip, superadmin_only
from app.models.lf_user import LfUser
from app.repositories.audit_repository import create_audit_log
from app.schemas.user import PasswordChange, UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    return db.query(LfUser).filter(LfUser.is_deleted == False).offset(skip).limit(limit).all()


@router.post("", response_model=UserResponse)
def create_user(
    body: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(superadmin_only),
):
    if db.query(LfUser).filter(LfUser.email == body.email).first():
        raise api_error("EMAIL_ALREADY_EXISTS")
    if db.query(LfUser).filter(LfUser.username == body.username).first():
        raise api_error("USERNAME_ALREADY_EXISTS")

    user = LfUser(
        email=body.email,
        username=body.username,
        password_hash=get_password_hash(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    create_audit_log(
        db, action="CREATE", actor_id=current["user"].user_id,
        entity_type="USER", entity_id=str(user.user_id),
        description=f"Usuario creado: {user.email}",
        actor_ip=get_client_ip(request),
    )
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(admin_or_superadmin),
):
    user = db.query(LfUser).filter(LfUser.user_id == user_id, LfUser.is_deleted == False).first()
    if not user:
        raise not_found_error("USER")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    body: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(superadmin_only),
):
    user = db.query(LfUser).filter(LfUser.user_id == user_id, LfUser.is_deleted == False).first()
    if not user:
        raise not_found_error("USER")

    old = {"email": user.email, "role": user.role, "is_active": user.is_active}
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)

    create_audit_log(
        db, action="UPDATE", actor_id=current["user"].user_id,
        entity_type="USER", entity_id=str(user.user_id),
        description=f"Usuario actualizado: {user.email}",
        old_values=old, new_values=body.model_dump(exclude_none=True),
        actor_ip=get_client_ip(request),
    )
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: dict = Depends(superadmin_only),
):
    user = db.query(LfUser).filter(LfUser.user_id == user_id, LfUser.is_deleted == False).first()
    if not user:
        raise not_found_error("USER")

    user.is_deleted = True
    user.is_active = False
    db.commit()

    create_audit_log(
        db, action="DELETE", actor_id=current["user"].user_id,
        entity_type="USER", entity_id=str(user_id),
        description=f"Usuario eliminado: {user.email}",
        actor_ip=get_client_ip(request),
    )
    return {"message": "Usuario eliminado correctamente"}
