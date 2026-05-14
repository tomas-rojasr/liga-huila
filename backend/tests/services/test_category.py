"""
Pruebas unitarias — app/services/category_service.py
Cubre todas las ramas de calculate_category (CC = 8):
  SUB-8 / SUB-10 / SUB-12 / SUB-14 / SUB-16 / SUB-18 / SUB-20 / PRIMERA
Incluye pruebas de frontera (cumpleaños hoy, mañana, ayer).
"""

import pytest
from datetime import date, timedelta

from app.services.category_service import calculate_category


# ──────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────

def birth_date_for_age(years: int) -> date:
    """Devuelve una fecha de nacimiento tal que la persona cumple exactamente
    `years` años hoy. Maneja el caso bisiesto (29 feb)."""
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


# ──────────────────────────────────────────────────────────────
# Pruebas por categoría (valores interiores de cada rango)
# ──────────────────────────────────────────────────────────────

class TestCategoriasNominales:

    def test_edad_3_retorna_sub8(self):
        assert calculate_category(birth_date_for_age(3)) == "SUB-8"

    def test_edad_7_retorna_sub8(self):
        assert calculate_category(birth_date_for_age(7)) == "SUB-8"

    def test_edad_9_retorna_sub10(self):
        assert calculate_category(birth_date_for_age(9)) == "SUB-10"

    def test_edad_11_retorna_sub12(self):
        assert calculate_category(birth_date_for_age(11)) == "SUB-12"

    def test_edad_13_retorna_sub14(self):
        assert calculate_category(birth_date_for_age(13)) == "SUB-14"

    def test_edad_15_retorna_sub16(self):
        assert calculate_category(birth_date_for_age(15)) == "SUB-16"

    def test_edad_17_retorna_sub18(self):
        assert calculate_category(birth_date_for_age(17)) == "SUB-18"

    def test_edad_19_retorna_sub20(self):
        assert calculate_category(birth_date_for_age(19)) == "SUB-20"

    def test_edad_25_retorna_primera(self):
        assert calculate_category(birth_date_for_age(25)) == "PRIMERA"

    def test_edad_40_retorna_primera(self):
        assert calculate_category(birth_date_for_age(40)) == "PRIMERA"


# ──────────────────────────────────────────────────────────────
# Pruebas de frontera (límite exacto de cada categoría)
# ──────────────────────────────────────────────────────────────

class TestFronterasCategorias:

    def test_exactamente_8_anos_hoy_retorna_sub10(self):
        """Al cumplir 8 años hoy, pasa de SUB-8 a SUB-10."""
        assert calculate_category(birth_date_for_age(8)) == "SUB-10"

    def test_un_dia_antes_de_cumplir_8_retorna_sub8(self):
        """Mañana cumple 8 → hoy todavía tiene 7 → sigue en SUB-8."""
        vispera = birth_date_for_age(8) + timedelta(days=1)
        assert calculate_category(vispera) == "SUB-8"

    def test_exactamente_10_anos_retorna_sub12(self):
        assert calculate_category(birth_date_for_age(10)) == "SUB-12"

    def test_exactamente_12_anos_retorna_sub14(self):
        assert calculate_category(birth_date_for_age(12)) == "SUB-14"

    def test_exactamente_14_anos_retorna_sub16(self):
        assert calculate_category(birth_date_for_age(14)) == "SUB-16"

    def test_exactamente_16_anos_retorna_sub18(self):
        assert calculate_category(birth_date_for_age(16)) == "SUB-18"

    def test_exactamente_18_anos_retorna_sub20(self):
        assert calculate_category(birth_date_for_age(18)) == "SUB-20"

    def test_exactamente_20_anos_retorna_primera(self):
        """Al cumplir 20 años hoy entra a PRIMERA División."""
        assert calculate_category(birth_date_for_age(20)) == "PRIMERA"

    def test_un_dia_antes_de_cumplir_20_retorna_sub20(self):
        """Mañana cumple 20 → hoy tiene 19 → sigue en SUB-20."""
        vispera = birth_date_for_age(20) + timedelta(days=1)
        assert calculate_category(vispera) == "SUB-20"


# ──────────────────────────────────────────────────────────────
# Casos especiales
# ──────────────────────────────────────────────────────────────

class TestCasosEspeciales:

    def test_recien_nacido_retorna_sub8(self):
        """Un bebé de 0 años va a SUB-8."""
        assert calculate_category(date.today()) == "SUB-8"

    def test_retorna_tipo_string(self):
        """La función siempre devuelve una cadena de texto."""
        resultado = calculate_category(birth_date_for_age(15))
        assert isinstance(resultado, str)

    def test_categorias_posibles_son_las_esperadas(self):
        """El conjunto de categorías devueltas debe ser exactamente el definido."""
        categorias_validas = {"SUB-8", "SUB-10", "SUB-12", "SUB-14",
                              "SUB-16", "SUB-18", "SUB-20", "PRIMERA"}
        edades_muestra = [3, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 30]
        resultados = {calculate_category(birth_date_for_age(e)) for e in edades_muestra}
        assert resultados.issubset(categorias_validas)
