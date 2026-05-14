"""
Pruebas unitarias — app/schemas/auth.py
Cubre: LoginRequest, TokenResponse, RefreshRequest
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest


class TestLoginRequest:

    def test_email_valido_y_password_crean_instancia(self):
        req = LoginRequest(email="admin@ligahuila.co", password="Clave123")
        assert req.email == "admin@ligahuila.co"
        assert req.password == "Clave123"

    def test_email_invalido_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="esto-no-es-email", password="Clave123")

    def test_email_sin_dominio_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="usuario@", password="Clave123")

    def test_password_vacio_se_acepta_como_string(self):
        """Pydantic no valida fortaleza — solo que el campo exista."""
        req = LoginRequest(email="admin@liga.co", password="")
        assert req.password == ""

    def test_falta_email_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="Clave123")

    def test_falta_password_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="admin@liga.co")

    def test_email_se_normaliza_a_minusculas(self):
        """Pydantic EmailStr normaliza el dominio a minúsculas."""
        req = LoginRequest(email="Admin@LIGA.CO", password="x")
        assert req.email == "Admin@liga.co"


class TestRefreshRequest:

    def test_refresh_token_valido(self):
        req = RefreshRequest(refresh_token="token-abc-123")
        assert req.refresh_token == "token-abc-123"

    def test_sin_refresh_token_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            RefreshRequest()


class TestTokenResponse:

    def test_token_response_completo(self):
        resp = TokenResponse(
            access_token="jwt.token.here",
            refresh_token="refresh-token-here",
            role="admin",
            user_id="uuid-123",
            email="admin@liga.co",
            full_name="Tomás Rojas",
        )
        assert resp.token_type == "bearer"
        assert resp.role == "admin"

    def test_token_type_por_defecto_es_bearer(self):
        resp = TokenResponse(
            access_token="a", refresh_token="b",
            role="consulta", user_id="x", email="x@x.co", full_name="X",
        )
        assert resp.token_type == "bearer"
