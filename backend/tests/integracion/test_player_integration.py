"""
Pruebas de Integración — Schema de Jugadores + Servicio de Categoría
Estrategia: Incremental Ascendente (módulos de bajo nivel ya probados unitariamente)

  MÓDULO A: schemas/player.py  (PlayerCreate — validación de datos)
        │
        ▼
  MÓDULO B: services/category_service.py  (calculate_category — lógica de negocio)

Se verifica que la integración entre la validación del schema y el cálculo
de categoría produce resultados coherentes end-to-end.
"""

import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from app.schemas.player import PlayerCreate
from app.services.category_service import calculate_category


# ──────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────

def birth_date_for_age(years: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


def jugador_con_edad(years: int, **kwargs) -> PlayerCreate:
    defaults = dict(
        first_name="Test",
        last_name="Jugador",
        birth_date=birth_date_for_age(years),
        document_number="1075000000",
    )
    defaults.update(kwargs)
    return PlayerCreate(**defaults)


# ──────────────────────────────────────────────────────────────
# Integración: schema acepta → category_service calcula
# ──────────────────────────────────────────────────────────────

class TestSchemaYCategoria:

    def test_jugador_7_anos_schema_valido_y_categoria_sub8(self):
        jugador = jugador_con_edad(7)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-8"

    def test_jugador_10_anos_schema_valido_y_categoria_sub12(self):
        jugador = jugador_con_edad(10)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-12"

    def test_jugador_15_anos_schema_valido_y_categoria_sub16(self):
        jugador = jugador_con_edad(15)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-16"

    def test_jugador_18_anos_schema_valido_y_categoria_sub20(self):
        jugador = jugador_con_edad(18)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-20"

    def test_jugador_25_anos_schema_valido_y_categoria_primera(self):
        jugador = jugador_con_edad(25)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "PRIMERA"

    def test_jugador_en_frontera_cumple_hoy_categoria_correcta(self):
        """Jugador que cumple exactamente 14 años hoy → SUB-16."""
        jugador = jugador_con_edad(14)
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-16"

    def test_jugador_un_dia_antes_de_cumplir_16_sigue_en_sub16(self):
        """Mañana cumple 16 → hoy tiene 15 → categoría SUB-16."""
        birth = birth_date_for_age(16) + timedelta(days=1)
        jugador = PlayerCreate(
            first_name="Test", last_name="J",
            birth_date=birth, document_number="123",
        )
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-16"


# ──────────────────────────────────────────────────────────────
# Integración: schema rechaza datos inválidos antes de llegar
# a la capa de negocio
# ──────────────────────────────────────────────────────────────

class TestValidacionAntesDeNegocio:

    def test_estado_invalido_no_llega_al_servicio(self):
        """El schema rechaza el estado antes de que se calcule la categoría."""
        with pytest.raises(ValidationError):
            jugador_con_edad(15, status="ELIMINADO")

    def test_tipo_documento_invalido_no_llega_al_servicio(self):
        with pytest.raises(ValidationError):
            jugador_con_edad(15, document_type="CEDULA")

    def test_datos_validos_llegan_al_servicio_sin_error(self):
        """Con datos válidos, schema + servicio trabajan sin excepción."""
        jugador = jugador_con_edad(13, status="ACTIVO", document_type="TI")
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-14"


# ──────────────────────────────────────────────────────────────
# Integración: consistencia entre estado y categoría
# ──────────────────────────────────────────────────────────────

class TestConsistenciaEstadoCategoria:

    def test_jugador_transferido_mantiene_categoria_correcta(self):
        """El estado TRANSFERIDO no afecta el cálculo de categoría."""
        jugador = jugador_con_edad(17, status="TRANSFERIDO")
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-18"

    def test_jugador_suspendido_mantiene_categoria_correcta(self):
        jugador = jugador_con_edad(19, status="SUSPENDIDO")
        categoria = calculate_category(jugador.birth_date)
        assert categoria == "SUB-20"

    def test_todos_los_estados_producen_la_misma_categoria(self):
        """La categoría depende solo de la edad, no del estado."""
        estados = ["ACTIVO", "INACTIVO", "SUSPENDIDO", "TRANSFERIDO"]
        categorias = set()
        for estado in estados:
            jugador = jugador_con_edad(16, status=estado)
            categorias.add(calculate_category(jugador.birth_date))
        assert len(categorias) == 1
        assert "SUB-18" in categorias
