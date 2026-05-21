"""
Pruebas de Partición Equivalente — Documento 13
Sistema de Gestión Liga de Fútbol del Huila
Fecha: 15 de mayo de 2026
Elaborado por: Tomás Rojas

Casos PE-01 a PE-25 — Módulos: Autenticación, Usuarios, Clubes, Jugadores, Categoría
"""

import pytest
from datetime import date
from pydantic import ValidationError
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.schemas.club import ClubCreate
from app.schemas.player import PlayerCreate
from app.services.category_service import calculate_category
from app.routes.auth import login
from app.core.security import get_password_hash


def birth_date_for_age(years: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


# ──────────────────────────────────────────────────────────────
# PE-01 a PE-05 — Autenticación: email y password
# ──────────────────────────────────────────────────────────────

class TestPE_Autenticacion:

    def test_PE01_email_valido_password_valida(self):
        """CV-01, CV-02: email con formato válido + password con caracteres → esquema aceptado."""
        body = LoginRequest(email="admin@liga.co", password="Clave2026!")
        assert body.email == "admin@liga.co"

    def test_PE02_email_sin_arroba_rechazado(self):
        """CI-01: email sin símbolo @ → ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="administrador.liga", password="Clave2026!")

    def test_PE03_email_vacio_rechazado(self):
        """CI-02: email vacío → ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="", password="Clave2026!")

    def test_PE04_password_con_espacios_y_texto_aceptada(self):
        """CV-03: password con espacios y texto mixto → esquema acepta correctamente."""
        body = LoginRequest(email="admin@liga.co", password="  Clave2026  ")
        assert body.password == "  Clave2026  "

    @patch("app.routes.auth.create_audit_log")
    def test_PE05_password_solo_espacios_debe_ser_rechazada(self, mock_audit):
        """CI-04: password compuesta solo de espacios → debe lanzar HTTP 400 PASSWORD_BLANK.
        FALLA — defecto DEF-AUT-001 abierto: el sistema autentica en lugar de rechazar."""
        from fastapi import HTTPException
        user = MagicMock()
        user.user_id = uuid4()
        user.email = "admin@liga.co"
        user.password_hash = get_password_hash("   ")
        user.is_active = True
        user.is_deleted = False
        user.locked_until = None
        user.failed_login_attempts = "0"
        user.role = "admin"
        user.first_name = "Admin"
        user.last_name = "Liga"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        req = MagicMock()
        req.headers.get.return_value = None
        req.client.host = "127.0.0.1"

        body = LoginRequest(email="admin@liga.co", password="   ")
        with pytest.raises(HTTPException) as exc_info:
            login(body, req, db)
        assert exc_info.value.status_code == 400


# ──────────────────────────────────────────────────────────────
# PE-06 a PE-11 — Usuarios: username y role
# ──────────────────────────────────────────────────────────────

class TestPE_Usuarios:

    def _usuario(self, **kwargs):
        defaults = dict(email="x@liga.co", username="tomas_rojas",
                        password="Clave123!", first_name="T", last_name="R")
        defaults.update(kwargs)
        return UserCreate(**defaults)

    def test_PE06_username_valido_aceptado(self):
        """CV-04: username con al menos un carácter → usuario creado."""
        u = self._usuario(username="tomas_rojas")
        assert u.username == "tomas_rojas"

    def test_PE07_username_vacio_rechazado(self):
        """CI-06: username vacío → ValidationError.
        FALLA — defecto DEF-USR-001 abierto: el sistema crea el usuario sin validar."""
        with pytest.raises(ValidationError):
            self._usuario(username="")

    def test_PE08_role_superadmin_aceptado(self):
        """CV-05: role 'superadmin' → válido."""
        assert self._usuario(role="superadmin").role == "superadmin"

    def test_PE09_role_admin_aceptado(self):
        """CV-06: role 'admin' → válido."""
        assert self._usuario(role="admin").role == "admin"

    def test_PE10_role_consulta_aceptado(self):
        """CV-07: role 'consulta' es el valor por defecto → válido."""
        assert self._usuario().role == "consulta"

    def test_PE11_role_invalido_rechazado(self):
        """CI-08: role desconocido → ValidationError — Rol inválido."""
        with pytest.raises(ValidationError):
            self._usuario(role="moderador")


# ──────────────────────────────────────────────────────────────
# PE-12 a PE-14 — Clubes: campo name
# ──────────────────────────────────────────────────────────────

class TestPE_Clubes:

    def test_PE12_nombre_valido_aceptado(self):
        """CV-08: nombre con texto → club creado correctamente."""
        c = ClubCreate(name="Atlético Neiva", code="ATN")
        assert c.name == "Atlético Neiva"

    def test_PE13_nombre_vacio_rechazado(self):
        """CI-10: nombre vacío → ValidationError.
        FALLA — defecto DEF-CLB-001 abierto: el sistema acepta nombre vacío."""
        with pytest.raises(ValidationError):
            ClubCreate(name="", code="ATN")

    def test_PE14_nombre_solo_espacios_rechazado(self):
        """CI-11: nombre con solo espacios → ValidationError.
        FALLA — defecto DEF-CLB-001 abierto: el sistema acepta solo espacios."""
        with pytest.raises(ValidationError):
            ClubCreate(name="   ", code="ATN")


# ──────────────────────────────────────────────────────────────
# PE-15 a PE-20 — Jugadores: document_type y status
# ──────────────────────────────────────────────────────────────

class TestPE_Jugadores:

    def _jugador(self, **kwargs):
        defaults = dict(first_name="T", last_name="R",
                        birth_date=birth_date_for_age(15), document_number="123")
        defaults.update(kwargs)
        return PlayerCreate(**defaults)

    def test_PE15_document_type_CC_aceptado(self):
        """CV-09: tipo CC válido."""
        assert self._jugador(document_type="CC").document_type == "CC"

    def test_PE16_document_type_TI_aceptado(self):
        """CV-10: tipo TI válido."""
        assert self._jugador(document_type="TI").document_type == "TI"

    def test_PE17_document_type_minuscula_rechazado(self):
        """CI-12: tipo en minúsculas ('cc') → ValidationError."""
        with pytest.raises(ValidationError):
            self._jugador(document_type="cc")

    def test_PE18_document_type_invalido_rechazado(self):
        """CI-13: tipo 'DNI' no contemplado → ValidationError."""
        with pytest.raises(ValidationError):
            self._jugador(document_type="DNI")

    def test_PE19_status_activo_aceptado(self):
        """CV-13: estado ACTIVO → válido."""
        assert self._jugador(status="ACTIVO").status == "ACTIVO"

    def test_PE20_status_invalido_rechazado(self):
        """CI-15: estado 'ELIMINADO' no válido → ValidationError."""
        with pytest.raises(ValidationError):
            self._jugador(status="ELIMINADO")


# ──────────────────────────────────────────────────────────────
# PE-21 a PE-25 — Categoría: edad del jugador
# ──────────────────────────────────────────────────────────────

class TestPE_Categoria:

    def test_PE21_edad_5_anos_sub8(self):
        """CV-17: edad < 8 → SUB-8."""
        assert calculate_category(birth_date_for_age(5)) == "SUB-8"

    def test_PE22_edad_11_anos_sub12(self):
        """CV-19: 10 ≤ edad < 12 → SUB-12."""
        assert calculate_category(birth_date_for_age(11)) == "SUB-12"

    def test_PE23_edad_15_anos_sub16(self):
        """CV-21: 14 ≤ edad < 16 → SUB-16."""
        assert calculate_category(birth_date_for_age(15)) == "SUB-16"

    def test_PE24_edad_19_anos_sub20(self):
        """CV-23: 18 ≤ edad < 20 → SUB-20."""
        assert calculate_category(birth_date_for_age(19)) == "SUB-20"

    def test_PE25_edad_25_anos_primera(self):
        """CV-24: edad ≥ 20 → PRIMERA."""
        assert calculate_category(birth_date_for_age(25)) == "PRIMERA"
