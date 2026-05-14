"""
Pruebas unitarias — app/schemas/player.py
Cubre: PlayerCreate (validate_doc_type, validate_status),
       PlayerUpdate (validate_status), constantes VALID_*
"""

import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas.player import (
    PlayerCreate,
    PlayerUpdate,
    VALID_STATUSES,
    VALID_POSITIONS,
    VALID_DOC_TYPES,
)


# ──────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────

def _jugador(**kwargs):
    defaults = dict(
        first_name="Sebastián",
        last_name="Sandoval",
        birth_date=date(2008, 3, 10),
        document_number="1075123456",
    )
    defaults.update(kwargs)
    return PlayerCreate(**defaults)


# ──────────────────────────────────────────────────────────────
# PlayerCreate — document_type
# ──────────────────────────────────────────────────────────────

class TestPlayerCreateDocType:

    def test_cc_valido(self):
        p = _jugador(document_type="CC")
        assert p.document_type == "CC"

    def test_ti_valido(self):
        p = _jugador(document_type="TI")
        assert p.document_type == "TI"

    def test_ce_valido(self):
        p = _jugador(document_type="CE")
        assert p.document_type == "CE"

    def test_pasaporte_valido(self):
        p = _jugador(document_type="PASAPORTE")
        assert p.document_type == "PASAPORTE"

    def test_tipo_invalido_lanza_validation_error(self):
        with pytest.raises(ValidationError, match="Tipo de documento inválido"):
            _jugador(document_type="DNI")

    def test_tipo_minusculas_invalido(self):
        with pytest.raises(ValidationError, match="Tipo de documento inválido"):
            _jugador(document_type="cc")

    def test_tipo_por_defecto_es_cc(self):
        p = _jugador()
        assert p.document_type == "CC"


# ──────────────────────────────────────────────────────────────
# PlayerCreate — status
# ──────────────────────────────────────────────────────────────

class TestPlayerCreateStatus:

    def test_activo_valido(self):
        p = _jugador(status="ACTIVO")
        assert p.status == "ACTIVO"

    def test_inactivo_valido(self):
        p = _jugador(status="INACTIVO")
        assert p.status == "INACTIVO"

    def test_suspendido_valido(self):
        p = _jugador(status="SUSPENDIDO")
        assert p.status == "SUSPENDIDO"

    def test_transferido_valido(self):
        p = _jugador(status="TRANSFERIDO")
        assert p.status == "TRANSFERIDO"

    def test_estado_invalido_lanza_validation_error(self):
        with pytest.raises(ValidationError, match="Estado inválido"):
            _jugador(status="ELIMINADO")

    def test_estado_minusculas_invalido(self):
        with pytest.raises(ValidationError, match="Estado inválido"):
            _jugador(status="activo")

    def test_estado_por_defecto_es_activo(self):
        p = _jugador()
        assert p.status == "ACTIVO"


# ──────────────────────────────────────────────────────────────
# PlayerCreate — campos requeridos y opcionales
# ──────────────────────────────────────────────────────────────

class TestPlayerCreateCampos:

    def test_sin_first_name_lanza_error(self):
        with pytest.raises(ValidationError):
            PlayerCreate(last_name="X", birth_date=date(2010, 1, 1), document_number="123")

    def test_sin_document_number_lanza_error(self):
        with pytest.raises(ValidationError):
            PlayerCreate(first_name="X", last_name="X", birth_date=date(2010, 1, 1))

    def test_team_id_opcional_es_none_por_defecto(self):
        p = _jugador()
        assert p.team_id is None

    def test_position_opcional_es_none_por_defecto(self):
        p = _jugador()
        assert p.position is None

    def test_nacionalidad_por_defecto_es_colombiana(self):
        p = _jugador()
        assert p.nationality == "Colombiana"


# ──────────────────────────────────────────────────────────────
# PlayerUpdate — validate_status
# ──────────────────────────────────────────────────────────────

class TestPlayerUpdate:

    def test_update_vacio_valido(self):
        """Todos los campos son opcionales en update."""
        update = PlayerUpdate()
        assert update.status is None

    def test_status_none_en_update_valido(self):
        update = PlayerUpdate(status=None)
        assert update.status is None

    def test_status_valido_en_update(self):
        update = PlayerUpdate(status="SUSPENDIDO")
        assert update.status == "SUSPENDIDO"

    def test_status_invalido_en_update_lanza_error(self):
        with pytest.raises(ValidationError, match="Estado inválido"):
            PlayerUpdate(status="BORRADO")


# ──────────────────────────────────────────────────────────────
# Constantes del módulo
# ──────────────────────────────────────────────────────────────

class TestConstantesPlayer:

    def test_valid_statuses_contiene_los_cuatro_estados(self):
        assert set(VALID_STATUSES) == {"ACTIVO", "INACTIVO", "SUSPENDIDO", "TRANSFERIDO"}

    def test_valid_doc_types_contiene_los_cuatro_tipos(self):
        assert set(VALID_DOC_TYPES) == {"CC", "TI", "CE", "PASAPORTE"}

    def test_valid_positions_contiene_las_cuatro_posiciones(self):
        assert set(VALID_POSITIONS) == {"Portero", "Defensa", "Mediocampista", "Delantero"}
