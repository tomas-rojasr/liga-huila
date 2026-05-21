"""
Pruebas de Integración — Módulo de Autenticación
Estrategia: Incremental Ascendente con Stub/Mock (ver material del profesor)

  SISTEMA PRINCIPAL (FastAPI app)
        │
        ▼
  MÓDULO A: routes/auth.py  ← componente bajo prueba
        │
        ├── security.py     ← módulo real (verify_password, create_access_token)
        ├── SQLAlchemy DB   ← STUB / MagicMock (simula llamado al módulo de datos)
        ├── Request         ← STUB / MagicMock (simula objeto HTTP)
        └── create_audit_log← STUB / patch (simula escritura de auditoría)

Se verifica que la lógica de integración entre la ruta y sus dependencias
produce los resultados correctos en cada escenario.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException

from app.routes.auth import login
from app.schemas.auth import LoginRequest
from app.core.security import get_password_hash


# ──────────────────────────────────────────────────────────────
# Fixtures compartidos
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def password_real():
    return "ClaveSegura2026!"


@pytest.fixture
def mock_user(password_real):
    """Stub de LfUser con credenciales válidas."""
    user = MagicMock()
    user.user_id = uuid4()
    user.email = "tomas@ligahuila.co"
    user.password_hash = get_password_hash(password_real)
    user.is_active = True
    user.is_deleted = False
    user.locked_until = None
    user.failed_login_attempts = "0"
    user.role = "admin"
    user.first_name = "Tomás"
    user.last_name = "Rojas"
    return user


@pytest.fixture
def mock_db(mock_user):
    """Stub de Session SQLAlchemy que devuelve mock_user al consultar."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_user
    return db


@pytest.fixture
def mock_request():
    """Stub de FastAPI Request sin cabecera x-forwarded-for."""
    req = MagicMock()
    req.headers.get.return_value = None      # sin proxy
    req.client.host = "127.0.0.1"
    return req


def _login_body(email="tomas@ligahuila.co", password="ClaveSegura2026!"):
    return LoginRequest(email=email, password=password)


# ──────────────────────────────────────────────────────────────
# Casos de prueba
# ──────────────────────────────────────────────────────────────

class TestLoginIntegracion:

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_retorna_access_token(self, mock_audit, mock_db, mock_request, password_real):
        """Integración completa: ruta → security → stub DB → respuesta."""
        body = _login_body(password=password_real)
        result = login(body, mock_request, mock_db)

        assert result.access_token is not None
        assert len(result.access_token) > 0

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_retorna_refresh_token(self, mock_audit, mock_db, mock_request, password_real):
        body = _login_body(password=password_real)
        result = login(body, mock_request, mock_db)

        assert result.refresh_token is not None
        assert result.token_type == "bearer"

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_retorna_datos_del_usuario(self, mock_audit, mock_db, mock_request, mock_user, password_real):
        body = _login_body(password=password_real)
        result = login(body, mock_request, mock_db)

        assert result.email == mock_user.email
        assert result.role == mock_user.role
        assert result.full_name == "Tomás Rojas"

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_registra_token_en_db(self, mock_audit, mock_db, mock_request, password_real):
        """Verifica que se llame db.add() y db.commit() para persistir el token."""
        body = _login_body(password=password_real)
        login(body, mock_request, mock_db)

        mock_db.add.assert_called_once()
        assert mock_db.commit.call_count >= 1

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_invoca_auditoria(self, mock_audit, mock_db, mock_request, password_real):
        """Verifica que se registre el evento LOGIN en el log de auditoría."""
        body = _login_body(password=password_real)
        login(body, mock_request, mock_db)

        mock_audit.assert_called_once()
        args, kwargs = mock_audit.call_args
        assert kwargs.get("action") == "LOGIN" or "LOGIN" in str(args)

    def test_login_usuario_no_encontrado_lanza_401(self, mock_db, mock_request):
        """Stub devuelve None → usuario inexistente → 401 INVALID_CREDENTIALS."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        body = _login_body()

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "INVALID_CREDENTIALS"

    def test_login_usuario_inactivo_lanza_401(self, mock_db, mock_request, mock_user):
        """Usuario con is_active=False → 401 USER_INACTIVE."""
        mock_user.is_active = False
        body = _login_body()

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "USER_INACTIVE"

    def test_login_cuenta_bloqueada_lanza_401(self, mock_db, mock_request, mock_user):
        """Usuario con locked_until en el futuro → 401 ACCOUNT_LOCKED."""
        mock_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=20)
        body = _login_body()

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "ACCOUNT_LOCKED"

    def test_login_bloqueo_expirado_permite_intento(self, mock_db, mock_request, mock_user, password_real):
        """Si locked_until ya pasó, debe dejar intentar (no lanzar ACCOUNT_LOCKED)."""
        mock_user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=5)
        body = _login_body(password="ClaveIncorrecta")

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, mock_db)

        # Debe fallar por credenciales, no por bloqueo
        assert exc_info.value.detail["code"] == "INVALID_CREDENTIALS"

    def test_login_password_incorrecta_lanza_401(self, mock_db, mock_request):
        """Contraseña equivocada → 401 INVALID_CREDENTIALS."""
        body = _login_body(password="ClaveEquivocada!")

        with pytest.raises(HTTPException) as exc_info:
            login(body, mock_request, mock_db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["code"] == "INVALID_CREDENTIALS"

    def test_login_password_incorrecta_incrementa_contador(self, mock_db, mock_request, mock_user):
        """Tras contraseña incorrecta, failed_login_attempts debe aumentar."""
        mock_user.failed_login_attempts = "1"
        body = _login_body(password="Mala")

        with pytest.raises(HTTPException):
            login(body, mock_request, mock_db)

        assert mock_user.failed_login_attempts == "2"

    def test_login_tercer_intento_fallido_bloquea_cuenta(self, mock_db, mock_request, mock_user):
        """Al tercer intento fallido se debe establecer locked_until."""
        mock_user.failed_login_attempts = "2"
        body = _login_body(password="MalaClave")

        with pytest.raises(HTTPException):
            login(body, mock_request, mock_db)

        assert mock_user.locked_until is not None
        assert mock_user.locked_until > datetime.now(timezone.utc)

    @patch("app.routes.auth.create_audit_log")
    def test_login_exitoso_resetea_intentos_fallidos(self, mock_audit, mock_db, mock_request, mock_user, password_real):
        """Login correcto después de intentos fallidos limpia el contador."""
        mock_user.failed_login_attempts = "2"
        body = _login_body(password=password_real)
        login(body, mock_request, mock_db)

        assert mock_user.failed_login_attempts == "0"
        assert mock_user.locked_until is None
