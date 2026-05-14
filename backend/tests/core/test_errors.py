"""
Pruebas unitarias — app/core/errors.py
Cubre: api_error, auth_error, not_found_error, forbidden_error
"""

import pytest
from fastapi import HTTPException

from app.core.errors import api_error, auth_error, not_found_error, forbidden_error


class TestApiError:

    def test_retorna_http_exception(self):
        exc = api_error("SOME_CODE")
        assert isinstance(exc, HTTPException)

    def test_status_code_por_defecto_es_400(self):
        exc = api_error("SOME_CODE")
        assert exc.status_code == 400

    def test_status_code_personalizado(self):
        exc = api_error("SOME_CODE", status_code=422)
        assert exc.status_code == 422

    def test_detail_contiene_code(self):
        exc = api_error("MI_CODIGO_ERROR")
        assert exc.detail["code"] == "MI_CODIGO_ERROR"

    def test_meta_por_defecto_es_dict_vacio(self):
        exc = api_error("SOME_CODE")
        assert exc.detail["meta"] == {}

    def test_meta_personalizado_se_incluye(self):
        meta = {"campo": "email", "mensaje": "ya existe"}
        exc = api_error("DUPLICATE", meta=meta)
        assert exc.detail["meta"] == meta


class TestAuthError:

    def test_status_code_es_401(self):
        exc = auth_error("INVALID_CREDENTIALS")
        assert exc.status_code == 401

    def test_code_se_propaga_correctamente(self):
        exc = auth_error("ACCOUNT_LOCKED")
        assert exc.detail["code"] == "ACCOUNT_LOCKED"

    def test_meta_con_locked_until(self):
        meta = {"locked_until": "2026-05-14T10:00:00Z"}
        exc = auth_error("ACCOUNT_LOCKED", meta=meta)
        assert exc.detail["meta"]["locked_until"] == "2026-05-14T10:00:00Z"

    def test_meta_por_defecto_es_dict_vacio(self):
        exc = auth_error("USER_INACTIVE")
        assert exc.detail["meta"] == {}


class TestNotFoundError:

    def test_status_code_es_404(self):
        exc = not_found_error("club")
        assert exc.status_code == 404

    def test_code_en_mayusculas_con_sufijo_not_found(self):
        exc = not_found_error("jugador")
        assert exc.detail["code"] == "JUGADOR_NOT_FOUND"

    def test_entidad_en_minusculas_se_convierte(self):
        exc = not_found_error("equipo")
        assert exc.detail["code"] == "EQUIPO_NOT_FOUND"


class TestForbiddenError:

    def test_status_code_es_403(self):
        exc = forbidden_error()
        assert exc.status_code == 403

    def test_code_por_defecto_es_forbidden(self):
        exc = forbidden_error()
        assert exc.detail["code"] == "FORBIDDEN"

    def test_code_personalizado(self):
        exc = forbidden_error("SOLO_SUPERADMIN")
        assert exc.detail["code"] == "SOLO_SUPERADMIN"
