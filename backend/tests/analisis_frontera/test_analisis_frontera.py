"""
Pruebas de Análisis de Frontera (Valores Límite) — Documento 14
Sistema de Gestión Liga de Fútbol del Huila
Fecha: 15 de mayo de 2026
Elaborado por: Tomás Rojas

Casos AF-01 a AF-22
Fronteras: categoría deportiva (7 puntos), intentos fallidos login (MAX=3), longitud campos
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.user import UserCreate
from app.schemas.club import ClubCreate
from app.services.category_service import calculate_category
from app.routes.auth import login
from app.core.security import get_password_hash


def exactamente(years: int) -> date:
    """Fecha de nacimiento para tener exactamente N años hoy."""
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


def un_dia_antes_de_cumplir(years: int) -> date:
    """Un día antes del cumpleaños número N → edad = N-1 años, 364 días."""
    return exactamente(years) + timedelta(days=1)


# ──────────────────────────────────────────────────────────────
# AF-01 a AF-14 — Fronteras de categoría deportiva
# ──────────────────────────────────────────────────────────────

class TestAF_FronterasCategoria:

    def test_AF01_un_dia_antes_de_cumplir_8_es_sub8(self):
        """F−1 frontera 8 años: 7a 364d → SUB-8."""
        assert calculate_category(un_dia_antes_de_cumplir(8)) == "SUB-8"

    def test_AF02_cumple_exactamente_8_es_sub10(self):
        """F frontera 8 años: 8a exactos → SUB-10 (operador estricto <)."""
        assert calculate_category(exactamente(8)) == "SUB-10"

    def test_AF03_un_dia_antes_de_cumplir_10_es_sub10(self):
        """F−1 frontera 10 años: 9a 364d → SUB-10."""
        assert calculate_category(un_dia_antes_de_cumplir(10)) == "SUB-10"

    def test_AF04_cumple_exactamente_10_es_sub12(self):
        """F frontera 10 años: 10a exactos → SUB-12."""
        assert calculate_category(exactamente(10)) == "SUB-12"

    def test_AF05_un_dia_antes_de_cumplir_12_es_sub12(self):
        """F−1 frontera 12 años: 11a 364d → SUB-12."""
        assert calculate_category(un_dia_antes_de_cumplir(12)) == "SUB-12"

    def test_AF06_cumple_exactamente_12_es_sub14(self):
        """F frontera 12 años: 12a exactos → SUB-14."""
        assert calculate_category(exactamente(12)) == "SUB-14"

    def test_AF07_un_dia_antes_de_cumplir_14_es_sub14(self):
        """F−1 frontera 14 años: 13a 364d → SUB-14."""
        assert calculate_category(un_dia_antes_de_cumplir(14)) == "SUB-14"

    def test_AF08_cumple_exactamente_14_es_sub16(self):
        """F frontera 14 años: 14a exactos → SUB-16."""
        assert calculate_category(exactamente(14)) == "SUB-16"

    def test_AF09_un_dia_antes_de_cumplir_16_es_sub16(self):
        """F−1 frontera 16 años: 15a 364d → SUB-16."""
        assert calculate_category(un_dia_antes_de_cumplir(16)) == "SUB-16"

    def test_AF10_cumple_exactamente_16_es_sub18(self):
        """F frontera 16 años: 16a exactos → SUB-18."""
        assert calculate_category(exactamente(16)) == "SUB-18"

    def test_AF11_un_dia_antes_de_cumplir_18_es_sub18(self):
        """F−1 frontera 18 años: 17a 364d → SUB-18."""
        assert calculate_category(un_dia_antes_de_cumplir(18)) == "SUB-18"

    def test_AF12_cumple_exactamente_18_es_sub20(self):
        """F frontera 18 años: 18a exactos → SUB-20."""
        assert calculate_category(exactamente(18)) == "SUB-20"

    def test_AF13_un_dia_antes_de_cumplir_20_es_sub20(self):
        """F−1 frontera 20 años: 19a 364d → SUB-20."""
        assert calculate_category(un_dia_antes_de_cumplir(20)) == "SUB-20"

    def test_AF14_cumple_exactamente_20_es_primera(self):
        """F frontera 20 años: 20a exactos → PRIMERA."""
        assert calculate_category(exactamente(20)) == "PRIMERA"


# ──────────────────────────────────────────────────────────────
# AF-15 a AF-18 — Frontera de intentos fallidos de login (MAX=3)
# ──────────────────────────────────────────────────────────────

class TestAF_IntentosLogin:

    def _setup(self, intentos_previos: int, bloqueado: bool = False):
        """Construye mock de usuario y db con N intentos previos."""
        from datetime import datetime, timezone, timedelta as td

        user = MagicMock()
        user.user_id = uuid4()
        user.email = "test@liga.co"
        user.password_hash = get_password_hash("correcta")
        user.is_active = True
        user.is_deleted = False
        user.failed_login_attempts = str(intentos_previos)
        user.first_name = "T"
        user.last_name = "R"
        user.role = "consulta"

        if bloqueado:
            user.locked_until = datetime.now(timezone.utc) + td(minutes=30)
        else:
            user.locked_until = None

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user

        req = MagicMock()
        req.headers.get.return_value = None
        req.client.host = "127.0.0.1"

        return user, db, req

    @patch("app.routes.auth.create_audit_log")
    def test_AF15_primer_intento_fallido_sin_bloqueo(self, mock_audit):
        """F−2: 1er intento fallido → contador sube a 1, sin bloqueo."""
        from app.schemas.auth import LoginRequest
        user, db, req = self._setup(intentos_previos=0)
        body = LoginRequest(email="test@liga.co", password="incorrecta")

        with pytest.raises(HTTPException) as exc:
            login(body, req, db)

        assert exc.value.status_code == 401
        assert user.failed_login_attempts == "1"
        assert user.locked_until is None

    @patch("app.routes.auth.create_audit_log")
    def test_AF16_segundo_intento_fallido_sin_bloqueo(self, mock_audit):
        """F−1: 2do intento fallido → contador sube a 2, sin bloqueo."""
        from app.schemas.auth import LoginRequest
        user, db, req = self._setup(intentos_previos=1)
        body = LoginRequest(email="test@liga.co", password="incorrecta")

        with pytest.raises(HTTPException) as exc:
            login(body, req, db)

        assert exc.value.status_code == 401
        assert user.failed_login_attempts == "2"
        assert user.locked_until is None

    @patch("app.routes.auth.create_audit_log")
    def test_AF17_tercer_intento_fallido_bloquea_cuenta(self, mock_audit):
        """F: 3er intento (MAX=3) → cuenta bloqueada 30 minutos."""
        from app.schemas.auth import LoginRequest
        user, db, req = self._setup(intentos_previos=2)
        body = LoginRequest(email="test@liga.co", password="incorrecta")

        with pytest.raises(HTTPException) as exc:
            login(body, req, db)

        assert exc.value.status_code == 401
        assert user.locked_until is not None

    @patch("app.routes.auth.create_audit_log")
    def test_AF18_intento_con_cuenta_bloqueada_rechazado(self, mock_audit):
        """F+1: cuenta ya bloqueada → HTTP 401 ACCOUNT_LOCKED."""
        from app.schemas.auth import LoginRequest
        user, db, req = self._setup(intentos_previos=0, bloqueado=True)
        body = LoginRequest(email="test@liga.co", password="cualquiera")

        with pytest.raises(HTTPException) as exc:
            login(body, req, db)

        assert exc.value.status_code == 401
        assert exc.value.detail["code"] == "ACCOUNT_LOCKED"


# ──────────────────────────────────────────────────────────────
# AF-19 a AF-22 — Frontera de longitud mínima en campos texto
# ──────────────────────────────────────────────────────────────

class TestAF_LongitudCampos:

    def test_AF19_username_longitud_0_rechazado(self):
        """F−1 longitud username: 0 chars → ValidationError.
        FALLA — DEF-USR-001 abierto: el sistema acepta username vacío."""
        with pytest.raises(ValidationError):
            UserCreate(email="x@liga.co", username="",
                       password="Clave123!", first_name="T", last_name="R")

    def test_AF20_username_longitud_1_aceptado(self):
        """F longitud username: 1 char → valor mínimo válido."""
        u = UserCreate(email="x@liga.co", username="a",
                       password="Clave123!", first_name="T", last_name="R")
        assert u.username == "a"

    def test_AF21_club_name_longitud_0_rechazado(self):
        """F−1 longitud name club: 0 chars → ValidationError.
        FALLA — DEF-CLB-001 abierto: el sistema acepta nombre vacío."""
        with pytest.raises(ValidationError):
            ClubCreate(name="", code="LFH")

    def test_AF22_club_name_longitud_1_aceptado(self):
        """F longitud name club: 1 char → valor mínimo válido."""
        c = ClubCreate(name="A", code="LFH")
        assert c.name == "A"
