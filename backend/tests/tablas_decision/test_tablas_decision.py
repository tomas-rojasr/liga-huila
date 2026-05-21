"""
Pruebas de Tablas de Decisión — Documento 17
Sistema de Gestión Liga de Fútbol del Huila
Fecha: 20 de mayo de 2026
Elaborado por: Nicolás (revisado y corregido por Tomás Rojas)

Casos TD-01 a TD-25
Tablas: T-01 (login), T-02 (categoría), T-04 (clubes), T-05 (jugadores)
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.auth import LoginRequest
from app.schemas.club import ClubCreate
from app.schemas.player import PlayerCreate
from app.schemas.user import UserCreate
from app.services.category_service import calculate_category
from app.routes.auth import login
from app.core.security import get_password_hash


def nacimiento_para_edad(years: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


# ──────────────────────────────────────────────────────────────
# T-01 — Tabla de decisión: intentos fallidos de login
# ──────────────────────────────────────────────────────────────

class TestTD_T01_Login:

    def _setup(self, intentos_previos: int, bloqueado: bool = False,
               password_correcta: bool = False):
        from datetime import datetime, timezone, timedelta as td

        user = MagicMock()
        user.user_id = uuid4()
        user.email = "jugador@liga.co"
        user.password_hash = get_password_hash("Clave123!")
        user.is_active = True
        user.is_deleted = False
        user.failed_login_attempts = str(intentos_previos)
        user.first_name = "N"
        user.last_name = "S"
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

        pwd = "Clave123!" if password_correcta else "incorrecta"
        body = LoginRequest(email="jugador@liga.co", password=pwd)

        return user, db, req, body

    @patch("app.routes.auth.create_audit_log")
    def test_TD01_credenciales_correctas_acceso_permitido(self, mock_audit):
        """T-01 R01: email válido + password correcta + cuenta activa → HTTP 200, token emitido."""
        user, db, req, body = self._setup(intentos_previos=0, password_correcta=True)
        result = login(body, req, db)
        assert result.access_token is not None
        assert result.role == "consulta"

    @patch("app.routes.auth.create_audit_log")
    def test_TD02_primer_intento_fallido_sin_bloqueo(self, mock_audit):
        """T-01 R02: 1er intento fallido → 401 INVALID_CREDENTIALS, contador = 1."""
        user, db, req, body = self._setup(intentos_previos=0)
        with pytest.raises(HTTPException) as exc:
            login(body, req, db)
        assert exc.value.status_code == 401
        assert user.failed_login_attempts == "1"
        assert user.locked_until is None

    @patch("app.routes.auth.create_audit_log")
    def test_TD03_segundo_intento_fallido_sin_bloqueo(self, mock_audit):
        """T-01 R03: 2do intento fallido → 401 INVALID_CREDENTIALS, contador = 2."""
        user, db, req, body = self._setup(intentos_previos=1)
        with pytest.raises(HTTPException) as exc:
            login(body, req, db)
        assert exc.value.status_code == 401
        assert user.failed_login_attempts == "2"
        assert user.locked_until is None

    @patch("app.routes.auth.create_audit_log")
    def test_TD04_tercer_intento_fallido_activa_bloqueo(self, mock_audit):
        """T-01 R04: 3er intento fallido (MAX=3) → 401, cuenta bloqueada 30 min."""
        user, db, req, body = self._setup(intentos_previos=2)
        with pytest.raises(HTTPException) as exc:
            login(body, req, db)
        assert exc.value.status_code == 401
        assert user.locked_until is not None

    @patch("app.routes.auth.create_audit_log")
    def test_TD05_cuenta_bloqueada_rechaza_cualquier_intento(self, mock_audit):
        """T-01 R05: cuenta bloqueada → 401 ACCOUNT_LOCKED sin importar la contraseña."""
        user, db, req, body = self._setup(intentos_previos=0, bloqueado=True)
        with pytest.raises(HTTPException) as exc:
            login(body, req, db)
        assert exc.value.status_code == 401
        assert exc.value.detail["code"] == "ACCOUNT_LOCKED"


# ──────────────────────────────────────────────────────────────
# T-02 — Tabla de decisión: categoría deportiva por edad
# Operador en código: < (estricto). Edad exacta N → categoría superior.
# ──────────────────────────────────────────────────────────────

class TestTD_T02_Categoria:

    def test_TD06_edad_5_anos_sub8(self):
        """T-02 R01: edad < 8 → SUB-8."""
        assert calculate_category(nacimiento_para_edad(5)) == "SUB-8"

    def test_TD07_edad_7_anos_sub8(self):
        """T-02 R02: 7 años (< 8) → SUB-8."""
        assert calculate_category(nacimiento_para_edad(7)) == "SUB-8"

    def test_TD08_edad_8_anos_exactos_sub10(self):
        """T-02 R03: 8 años exactos → SUB-10 (operador < estricto)."""
        assert calculate_category(nacimiento_para_edad(8)) == "SUB-10"

    def test_TD09_edad_9_anos_sub10(self):
        """T-02 R04: 9 años → SUB-10."""
        assert calculate_category(nacimiento_para_edad(9)) == "SUB-10"

    def test_TD10_edad_10_anos_exactos_sub12(self):
        """T-02 R05: 10 años exactos → SUB-12."""
        assert calculate_category(nacimiento_para_edad(10)) == "SUB-12"

    def test_TD11_edad_11_anos_sub12(self):
        """T-02 R06: 11 años → SUB-12."""
        assert calculate_category(nacimiento_para_edad(11)) == "SUB-12"

    def test_TD12_edad_12_anos_exactos_sub14(self):
        """T-02 R07: 12 años exactos → SUB-14."""
        assert calculate_category(nacimiento_para_edad(12)) == "SUB-14"

    def test_TD13_edad_14_anos_exactos_sub16(self):
        """T-02 R08: 14 años exactos → SUB-16."""
        assert calculate_category(nacimiento_para_edad(14)) == "SUB-16"

    def test_TD14_edad_16_anos_exactos_sub18(self):
        """T-02 R09: 16 años exactos → SUB-18."""
        assert calculate_category(nacimiento_para_edad(16)) == "SUB-18"

    def test_TD15_edad_18_anos_exactos_sub20(self):
        """T-02 R10: 18 años exactos → SUB-20."""
        assert calculate_category(nacimiento_para_edad(18)) == "SUB-20"

    def test_TD16_edad_20_anos_exactos_primera(self):
        """T-02 R11: 20 años exactos → PRIMERA."""
        assert calculate_category(nacimiento_para_edad(20)) == "PRIMERA"

    def test_TD17_edad_25_anos_primera(self):
        """T-02 R12: 25 años → PRIMERA."""
        assert calculate_category(nacimiento_para_edad(25)) == "PRIMERA"


# ──────────────────────────────────────────────────────────────
# T-04 — Tabla de decisión: creación de club
# ──────────────────────────────────────────────────────────────

class TestTD_T04_Clubes:

    def test_TD18_club_datos_completos_valido(self):
        """T-04 R01: nombre, código y dirección válidos → ClubCreate aceptado."""
        c = ClubCreate(name="Atlético Neiva", code="ATN",
                       address="Cra 5 #10-20, Neiva")
        assert c.name == "Atlético Neiva"
        assert c.code == "ATN"
        assert c.address == "Cra 5 #10-20, Neiva"

    def test_TD19_club_sin_campos_opcionales_valido(self):
        """T-04 R02: solo nombre y código → campos opcionales en None."""
        c = ClubCreate(name="Deportivo Pitalito", code="DPI")
        assert c.address is None
        assert c.phone is None
        assert c.email is None

    def test_TD20_club_nombre_vacio_rechazado(self):
        """T-04 R03: nombre vacío → ValidationError.
        FALLA — DEF-CLB-001 abierto: el sistema acepta nombre vacío."""
        with pytest.raises(ValidationError):
            ClubCreate(name="", code="ATN")

    def test_TD21_club_nombre_solo_espacios_rechazado(self):
        """T-04 R04: nombre con solo espacios → ValidationError.
        FALLA — DEF-CLB-001 abierto: el sistema acepta solo espacios."""
        with pytest.raises(ValidationError):
            ClubCreate(name="   ", code="ATN")


# ──────────────────────────────────────────────────────────────
# T-05 — Tabla de decisión: tipo de documento del jugador
# Nota: document_number no tiene validación de formato en el sistema actual.
# ──────────────────────────────────────────────────────────────

class TestTD_T05_DocumentoJugador:

    def _jugador(self, **kwargs):
        defaults = dict(first_name="N", last_name="S",
                        birth_date=nacimiento_para_edad(15),
                        document_number="123456789")
        defaults.update(kwargs)
        return PlayerCreate(**defaults)

    def test_TD22_tipo_CC_aceptado(self):
        """T-05 R01: document_type='CC' → válido."""
        assert self._jugador(document_type="CC").document_type == "CC"

    def test_TD23_tipo_TI_aceptado(self):
        """T-05 R02: document_type='TI' → válido."""
        assert self._jugador(document_type="TI").document_type == "TI"

    def test_TD24_tipo_CE_aceptado(self):
        """T-05 R03: document_type='CE' → válido."""
        assert self._jugador(document_type="CE").document_type == "CE"

    def test_TD25_tipo_invalido_rechazado(self):
        """T-05 R04: document_type desconocido → ValidationError."""
        with pytest.raises(ValidationError):
            self._jugador(document_type="DNI")
