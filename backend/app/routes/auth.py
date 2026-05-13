from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import auth_error
from app.core.security import (
    MAX_FAILED_LOGIN_ATTEMPTS,
    ACCOUNT_LOCK_DURATION,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.dependencies.auth import get_client_ip, get_current_user
from app.models.lf_auth_token import LfAuthToken
from app.models.lf_user import LfUser
from app.repositories.audit_repository import create_audit_log
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(LfUser).filter(LfUser.email == body.email, LfUser.is_deleted == False).first()

    if not user:
        raise auth_error("INVALID_CREDENTIALS")

    if not user.is_active:
        raise auth_error("USER_INACTIVE")

    now = datetime.now(timezone.utc)

    if user.locked_until and user.locked_until > now:
        raise auth_error("ACCOUNT_LOCKED", meta={"locked_until": user.locked_until.isoformat()})

    if not verify_password(body.password, user.password_hash):
        attempts = int(user.failed_login_attempts or "0") + 1
        user.failed_login_attempts = str(attempts)
        if attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = now + ACCOUNT_LOCK_DURATION
            user.failed_login_attempts = "0"
        db.commit()
        raise auth_error("INVALID_CREDENTIALS")

    user.failed_login_attempts = "0"
    user.locked_until = None
    db.commit()

    access_token = create_access_token(str(user.user_id), user.role)
    refresh_token = create_refresh_token()

    token_record = LfAuthToken(
        user_id=user.user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=now + timedelta(days=7),
    )
    db.add(token_record)
    db.commit()

    ip = get_client_ip(request)
    create_audit_log(db, action="LOGIN", actor_id=user.user_id, entity_type="USER",
                     entity_id=str(user.user_id), description="Inicio de sesión", actor_ip=ip)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=str(user.user_id),
        email=user.email,
        full_name=f"{user.first_name} {user.last_name}",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    token_record = (
        db.query(LfAuthToken)
        .filter(LfAuthToken.refresh_token == body.refresh_token, LfAuthToken.is_revoked == False)
        .first()
    )
    if not token_record:
        raise auth_error("INVALID_REFRESH_TOKEN")

    now = datetime.now(timezone.utc)
    if token_record.expires_at < now:
        token_record.is_revoked = True
        db.commit()
        raise auth_error("REFRESH_TOKEN_EXPIRED")

    user = db.query(LfUser).filter(LfUser.user_id == token_record.user_id, LfUser.is_active == True).first()
    if not user:
        raise auth_error("USER_NOT_FOUND_OR_INACTIVE")

    token_record.is_revoked = True
    db.commit()

    new_access = create_access_token(str(user.user_id), user.role)
    new_refresh = create_refresh_token()

    new_record = LfAuthToken(
        user_id=user.user_id,
        access_token=new_access,
        refresh_token=new_refresh,
        expires_at=now + timedelta(days=7),
    )
    db.add(new_record)
    db.commit()

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        role=user.role,
        user_id=str(user.user_id),
        email=user.email,
        full_name=f"{user.first_name} {user.last_name}",
    )


@router.post("/logout")
def logout(current: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    token_record = current["token"]
    token_record.is_revoked = True
    db.commit()

    user = current["user"]
    create_audit_log(db, action="LOGOUT", actor_id=user.user_id, entity_type="USER",
                     entity_id=str(user.user_id), description="Cierre de sesión")

    return {"message": "Sesión cerrada correctamente"}


@router.get("/me")
def get_me(current: dict = Depends(get_current_user)):
    user = current["user"]
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
    }
