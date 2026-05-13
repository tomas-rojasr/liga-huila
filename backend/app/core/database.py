from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_models():
    from app.models import (  # noqa: F401
        lf_user,
        lf_auth_token,
        lf_club,
        lf_team,
        lf_player,
        lf_audit_log,
    )
