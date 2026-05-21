"""
Pruebas unitarias — app/schemas/user.py
Cubre: UserCreate (validate_role), UserUpdate (validate_role), PasswordChange
"""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate, PasswordChange


# ──────────────────────────────────────────────────────────────
# UserCreate
# ──────────────────────────────────────────────────────────────

class TestUserCreate:

    def _base(self, **kwargs):
        defaults = dict(
            email="nicolas@liga.co",
            username="njime",
            password="Pass123!",
            first_name="Nicolás",
            last_name="Jiménez",
        )
        defaults.update(kwargs)
        return UserCreate(**defaults)

    def test_rol_superadmin_valido(self):
        user = self._base(role="superadmin")
        assert user.role == "superadmin"

    def test_rol_admin_valido(self):
        user = self._base(role="admin")
        assert user.role == "admin"

    def test_rol_consulta_valido(self):
        user = self._base(role="consulta")
        assert user.role == "consulta"

    def test_rol_por_defecto_es_consulta(self):
        user = self._base()
        assert user.role == "consulta"

    def test_rol_invalido_lanza_validation_error(self):
        with pytest.raises(ValidationError, match="Rol inválido"):
            self._base(role="root")

    def test_rol_mayusculas_invalido(self):
        with pytest.raises(ValidationError, match="Rol inválido"):
            self._base(role="ADMIN")

    def test_email_invalido_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            self._base(email="no-es-email")

    def test_falta_username_lanza_validation_error(self):
        with pytest.raises(ValidationError):
            UserCreate(email="x@x.co", password="x", first_name="X", last_name="X")

    def test_campos_requeridos_se_asignan(self):
        user = self._base()
        assert user.first_name == "Nicolás"
        assert user.last_name == "Jiménez"
        assert user.username == "njime"


# ──────────────────────────────────────────────────────────────
# UserUpdate
# ──────────────────────────────────────────────────────────────

class TestUserUpdate:

    def test_todos_los_campos_opcionales(self):
        """UserUpdate sin campos no lanza error."""
        update = UserUpdate()
        assert update.role is None
        assert update.email is None

    def test_rol_valido_en_update(self):
        update = UserUpdate(role="admin")
        assert update.role == "admin"

    def test_rol_invalido_en_update_lanza_error(self):
        with pytest.raises(ValidationError, match="Rol inválido"):
            UserUpdate(role="hacker")

    def test_rol_none_en_update_es_valido(self):
        """No enviar rol (None) no debe lanzar error."""
        update = UserUpdate(role=None)
        assert update.role is None

    def test_is_active_se_puede_actualizar(self):
        update = UserUpdate(is_active=False)
        assert update.is_active is False


# ──────────────────────────────────────────────────────────────
# PasswordChange
# ──────────────────────────────────────────────────────────────

class TestPasswordChange:

    def test_instancia_valida(self):
        pc = PasswordChange(current_password="Vieja123", new_password="Nueva456!")
        assert pc.current_password == "Vieja123"
        assert pc.new_password == "Nueva456!"

    def test_falta_current_password_lanza_error(self):
        with pytest.raises(ValidationError):
            PasswordChange(new_password="Nueva456!")

    def test_falta_new_password_lanza_error(self):
        with pytest.raises(ValidationError):
            PasswordChange(current_password="Vieja123")
