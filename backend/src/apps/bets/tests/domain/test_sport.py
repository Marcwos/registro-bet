"""
Tests de dominio — Entidad: Sport

La entidad Sport es un dataclass. Testeamos:
  - Que se puede crear con datos válidos
  - Que sus propiedades almacenan los valores correctos
  - Que el estado activo/inactivo funciona
"""

from uuid import uuid4

from ...domain.entities.sport import Sport


class TestSport:
    def test_create_sport_with_valid_data(self):
        """Un Sport se crea correctamente con todos los campos."""
        sport_id = uuid4()
        sport = Sport(id=sport_id, name="Fútbol", is_active=True)

        assert sport.id == sport_id
        assert sport.name == "Fútbol"
        assert sport.is_active is True

    def test_sport_can_be_inactive(self):
        """Un Sport puede estar inactivo."""
        sport = Sport(id=uuid4(), name="Cricket", is_active=False)
        assert sport.is_active is False

    def test_sport_name_is_stored_correctly(self):
        """El nombre se almacena tal cual se proporciona."""
        sport = Sport(id=uuid4(), name="MMA", is_active=True)
        assert sport.name == "MMA"
