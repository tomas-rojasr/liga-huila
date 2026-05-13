from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import auth_error, forbidden_error
from app.core.security import decode_access_token
from app.models.lf_auth_token import LfAuthToken
from app.models.lf_user import LfUser

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    token_str = credentials.credentials

    try:
        payload = decode_access_token(token_str)
    except ValueError:
        raise auth_error("TOKEN_INVALID")

    user_id = payload.get("sub")
    role = payload.get("role")

    token_record = (
        db.query(LfAuthToken)
        .filter(
            LfAuthToken.access_token == token_str,
            LfAuthToken.is_revoked == False,
        )
        .first()
    )
    if not token_record:
        raise auth_error("TOKEN_REVOKED_OR_NOT_FOUND")

    user = db.query(LfUser).filter(LfUser.user_id == user_id, LfUser.is_active == True).first()
    if not user:
        raise auth_error("USER_NOT_FOUND_OR_INACTIVE")

    return {"user": user, "token": token_record, "role": role}


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def require_roles(*roles: str):
    def dependency(current: dict = Depends(get_current_user)):
        if current["role"] not in roles:
            raise forbidden_error("INSUFFICIENT_ROLE")
        return current
    return dependency


def superadmin_only(current: dict = Depends(get_current_user)):
    if current["role"] != "superadmin":
        raise forbidden_error("SUPERADMIN_REQUIRED")
    return current


def admin_or_superadmin(current: dict = Depends(get_current_user)):
    if current["role"] not in ("admin", "superadmin"):
        raise forbidden_error("ADMIN_REQUIRED")
    return current
