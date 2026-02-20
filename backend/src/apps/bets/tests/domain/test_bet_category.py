"""
Tests de dominio — Entidad: BetCategory

Testeamos:
  - Creación con datos válidos
  - Que la descripción puede estar vacía
  - Que los valores se almacenan correctamente
"""

from uuid import uuid4

from ...domain.entities.bet_category import BetCategory


class TestBetCategory:
    def test_create_category_with_valid_data(self):
        """Una BetCategory se crea correctamente."""
        cat_id = uuid4()
        category = BetCategory(id=cat_id, name="Simple", description="Apuesta simple")

        assert category.id == cat_id
        assert category.name == "Simple"
        assert category.description == "Apuesta simple"

    def test_category_with_empty_description(self):
        """La descripción puede estar vacía."""
        category = BetCategory(id=uuid4(), name="Combinada de 2", description="")
        assert category.description == ""

    def test_category_name_stored_correctly(self):
        """El nombre se almacena tal cual."""
        category = BetCategory(id=uuid4(), name="Combinada (3-5)", description="De 3 a 5 selecciones")
        assert category.name == "Combinada (3-5)"
