"""
Pruebas de Regresión — Verificación de defectos reportados
Cada prueba corresponde a un defecto del Reporte de Errores.
Si una prueba FALLA, significa que el defecto sigue presente en el código.

DEF-AUT-001 — Login acepta contraseña con solo espacios en blanco
DEF-CLB-001 — Registro de club permite nombre vacío
DEF-USR-001 (parcial) — UserCreate acepta nombre de usuario vacío
"""

import pytest
from datetime import timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.routes.auth import login
from app.schemas.auth import LoginRequest
from app.schemas.club import ClubCreate
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def mock_request():
    req = MagicMock()
    req.headers.get.return_value = None
    req.client.host = "127.0.0.1"
    return req


@pytest.fixture
def db_con_usuario_espacios():
    """Simula un usuario cuya contraseña fue registrada como '   ' (solo espacios).
    Este es el escenario exacto del DEF-AUT-001."""
    user = MagicMock()
    user.user_id = uuid4()
    user.email = "victima@liga.co"
    user.password_hash = get_password_hash("   ")   # ← contraseña registrada con espacios
    user.is_active = True
    user.is_deleted = False
    user.locked_until = None
    user.failed_login_attempts = "0"
    user.role = "admin"
    user.first_name = "Usuario"
    user.last_name = "Prueba"

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = user
    return db


# ──────────────────────────────────────────────────────────────
# DEF-AUT-001
# Login acepta contraseña con solo espacios en blanco
# Estado en reporte: Cerrado QA — arreglado por Tomás Rojas (compilación 1.1)
# Verificación: ¿el backend realmente valida antes de llamar a bcrypt?
# ──────────────────────────────────────────────────────────────

class TestDefAut001:

    @patch("app.routes.auth.create_audit_log")
    def test_password_solo_espacios_debe_ser_rechazado(
        self, mock_audit, db_con_usuario_espacios, mock_request
    ):
        """
        El sistema NO debe autenticar a un usuario si la contraseña
        enviada es únicamente espacios en blanco, incluso si el hash coincide.
        Se espera un error 400 con código PASSWORD_BLANK.
        """
        body = LoginRequest(email="victima@liga.co", password="   ")

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, db_con_usuario_espacios)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["code"] == "PASSWORD_BLANK"

    @patch("app.routes.auth.create_audit_log")
    def test_password_con_espacios_y_texto_si_se_acepta(
        self, mock_audit, mock_request
    ):
        """Una contraseña con espacios y texto válido sí debe autenticarse."""
        user = MagicMock()
        user.user_id = uuid4()
        user.email = "x@liga.co"
        user.password_hash = get_password_hash("  Clave2026  ")
        user.is_active = True
        user.is_deleted = False
        user.locked_until = None
        user.failed_login_attempts = "0"
        user.role = "consulta"
        user.first_name = "X"
        user.last_name = "Y"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        body = LoginRequest(email="x@liga.co", password="  Clave2026  ")
        result = login(body, mock_request, db)
        assert result.access_token is not None


# ──────────────────────────────────────────────────────────────
# DEF-CLB-001
# Registro de club permite nombre vacío
# Estado en reporte: Cerrado QA — arreglado por Tomás Rojas (compilación 1.1)
# ──────────────────────────────────────────────────────────────

class TestDefClb001:

    def test_nombre_club_vacio_debe_fallar(self):
        """
        ClubCreate con name='' debe lanzar ValidationError.
        Un club sin nombre no tiene sentido y genera registros inválidos en la BD.
        """
        with pytest.raises(ValidationError):
            ClubCreate(name="", code="LFH")

    def test_nombre_club_solo_espacios_debe_fallar(self):
        """Nombre con solo espacios también debe ser rechazado."""
        with pytest.raises(ValidationError):
            ClubCreate(name="   ", code="LFH")

    def test_nombre_club_valido_se_acepta(self):
        """Nombre real debe funcionar sin problema."""
        club = ClubCreate(name="Atlético Neiva", code="ATN")
        assert club.name == "Atlético Neiva"


# ──────────────────────────────────────────────────────────────
# DEF-USR-001 (parcial) — Validación de campos requeridos en usuarios
# ──────────────────────────────────────────────────────────────

class TestDefUsr001:

    def test_username_vacio_debe_fallar(self):
        """
        UserCreate con username='' debe lanzar ValidationError.
        Un usuario sin nombre de usuario no puede iniciar sesión.
        """
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@liga.co",
                username="",
                password="Clave123!",
                first_name="Test",
                last_name="User",
            )

    def test_username_valido_se_acepta(self):
        user = UserCreate(
            email="tomas@liga.co",
            username="tomas_rojas",
            password="Clave123!",
            first_name="Tomás",
            last_name="Rojas",
        )
        assert user.username == "tomas_rojas"
