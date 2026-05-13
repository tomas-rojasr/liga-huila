"""
Ejecutar una sola vez para crear el usuario superadministrador inicial.
Uso: python seed.py
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal, import_models
from app.core.security import get_password_hash
from app.models.lf_user import LfUser

import_models()


def seed():
    db = SessionLocal()
    try:
        existing = db.query(LfUser).filter(LfUser.email == "admin@ligahuila.com").first()
        if existing:
            print("El usuario superadmin ya existe. No se creó ninguno nuevo.")
            return

        superadmin = LfUser(
            email="admin@ligahuila.com",
            username="superadmin",
            password_hash=get_password_hash("Admin123!"),
            first_name="Super",
            last_name="Administrador",
            role="superadmin",
            is_active=True,
        )
        db.add(superadmin)
        db.commit()
        print("=" * 50)
        print("Usuario superadmin creado exitosamente.")
        print("  Email:      admin@ligahuila.com")
        print("  Contraseña: Admin123!")
        print("  Rol:        superadmin")
        print("IMPORTANTE: Cambia la contraseña después del primer login.")
        print("=" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
