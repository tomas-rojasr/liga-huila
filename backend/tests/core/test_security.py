"""
Pruebas unitarias — app/core/security.py
Cubre: get_password_hash, verify_password, create_access_token,
       decode_access_token, create_refresh_token
"""

import pytest
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    MAX_FAILED_LOGIN_ATTEMPTS,
    ACCOUNT_LOCK_DURATION,
)
from app.core.config import settings


# ──────────────────────────────────────────────────────────────
# Utilidades de apoyo
# ──────────────────────────────────────────────────────────────

def _make_expired_token(subject: str = "test-user", role: str = "admin") -> str:
    """Crea un JWT con fecha de expiración en el pasado."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": now - timedelta(hours=2),
        "nbf": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),   # expirado hace 1 hora
        "iss": "liga-futbol-huila",
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _make_token_wrong_type(subject: str = "test-user", role: str = "admin") -> str:
    """Crea un JWT con type='refresh' en lugar de 'access'."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(hours=8),
        "iss": "liga-futbol-huila",
        "type": "refresh",               # tipo incorrecto
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ──────────────────────────────────────────────────────────────
# get_password_hash
# ──────────────────────────────────────────────────────────────

class TestGetPasswordHash:

    def test_retorna_cadena_no_vacia(self):
        hashed = get_password_hash("Clave123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_es_diferente_al_texto_original(self):
        password = "MiContraseña2026"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_mismo_password_genera_hashes_distintos(self):
        """bcrypt usa sal aleatoria: dos hashes del mismo texto deben diferir."""
        password = "MismaClaveDobleHash"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2


# ──────────────────────────────────────────────────────────────
# verify_password
# ──────────────────────────────────────────────────────────────

class TestVerifyPassword:

    def setup_method(self):
        self.password = "ClaveSegura#99"
        self.hashed = get_password_hash(self.password)

    def test_contrasena_correcta_retorna_true(self):
        assert verify_password(self.password, self.hashed) is True

    def test_contrasena_incorrecta_retorna_false(self):
        assert verify_password("ClaveEquivocada", self.hashed) is False

    def test_contrasena_vacia_retorna_false(self):
        assert verify_password("", self.hashed) is False

    def test_contrasena_solo_espacios_retorna_false(self):
        """Relacionado con DEF-AUT-001: espacios en blanco no deben autenticar."""
        assert verify_password("     ", self.hashed) is False

    def test_contrasena_similar_pero_diferente_retorna_false(self):
        """Un carácter de diferencia debe fallar."""
        assert verify_password("ClaveSegura#9", self.hashed) is False

    def test_contrasena_case_sensitive(self):
        """La verificación debe ser sensible a mayúsculas."""
        assert verify_password("clavesegura#99", self.hashed) is False

    def test_contrasena_con_espacios_al_inicio(self):
        assert verify_password(" ClaveSegura#99", self.hashed) is False


# ──────────────────────────────────────────────────────────────
# create_access_token
# ──────────────────────────────────────────────────────────────

class TestCreateAccessToken:

    def setup_method(self):
        self.user_id = "abc-123-uuid"
        self.role = "admin"
        self.token = create_access_token(self.user_id, self.role)

    def test_retorna_cadena_no_vacia(self):
        assert isinstance(self.token, str)
        assert len(self.token) > 0

    def test_payload_contiene_sub_correcto(self):
        payload = decode_access_token(self.token)
        assert payload["sub"] == self.user_id

    def test_payload_contiene_role_correcto(self):
        payload = decode_access_token(self.token)
        assert payload["role"] == self.role

    def test_payload_type_es_access(self):
        payload = decode_access_token(self.token)
        assert payload["type"] == "access"

    def test_payload_issuer_correcto(self):
        payload = decode_access_token(self.token)
        assert payload["iss"] == "liga-futbol-huila"

    def test_dos_tokens_distintos_para_mismo_usuario(self):
        """Cada token lleva un jti único."""
        token2 = create_access_token(self.user_id, self.role)
        assert self.token != token2

    def test_token_roles_distintos_generan_tokens_distintos(self):
        token_superadmin = create_access_token(self.user_id, "superadmin")
        token_admin = create_access_token(self.user_id, "admin")
        assert token_superadmin != token_admin


# ──────────────────────────────────────────────────────────────
# decode_access_token
# ──────────────────────────────────────────────────────────────

class TestDecodeAccessToken:

    def test_token_valido_decodifica_correctamente(self):
        token = create_access_token("usuario-xyz", "consulta")
        payload = decode_access_token(token)
        assert payload["sub"] == "usuario-xyz"
        assert payload["role"] == "consulta"

    def test_token_expirado_lanza_value_error(self):
        token = _make_expired_token()
        with pytest.raises(ValueError, match="Token inválido"):
            decode_access_token(token)

    def test_token_manipulado_lanza_value_error(self):
        token = create_access_token("usuario-xyz", "admin")
        token_corrupto = token[:-5] + "XXXXX"
        with pytest.raises(ValueError, match="Token inválido"):
            decode_access_token(token_corrupto)

    def test_token_tipo_incorrecto_lanza_value_error(self):
        token = _make_token_wrong_type()
        with pytest.raises(ValueError, match="Token inválido"):
            decode_access_token(token)

    def test_cadena_aleatoria_lanza_value_error(self):
        with pytest.raises(ValueError, match="Token inválido"):
            decode_access_token("esto.no.es.un.jwt")

    def test_token_vacio_lanza_value_error(self):
        with pytest.raises((ValueError, Exception)):
            decode_access_token("")


# ──────────────────────────────────────────────────────────────
# create_refresh_token
# ──────────────────────────────────────────────────────────────

class TestCreateRefreshToken:

    def test_retorna_cadena_no_vacia(self):
        token = create_refresh_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_cada_token_es_unico(self):
        tokens = {create_refresh_token() for _ in range(10)}
        assert len(tokens) == 10


# ──────────────────────────────────────────────────────────────
# Constantes de configuración de seguridad
# ──────────────────────────────────────────────────────────────

class TestSecurityConstants:

    def test_max_intentos_fallidos_es_tres(self):
        assert MAX_FAILED_LOGIN_ATTEMPTS == 3

    def test_duracion_bloqueo_es_30_minutos(self):
        assert ACCOUNT_LOCK_DURATION == timedelta(minutes=30)
