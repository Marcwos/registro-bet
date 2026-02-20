"""
Tests — Use Case: CreateSport

Testeamos:
  - Crear deporte exitosamente
  - Falla si ya existe un deporte con ese nombre
"""

from unittest.mock import Mock

import pytest

from ...application.use_cases.create_sport import CreateSport
from ...domain.exceptions import SportAlreadyExistsException
from ...domain.repositories.sport_repository import SportRepository


class TestCreateSport:
    def setup_method(self):
        self.repository = Mock(spec=SportRepository)
        self.use_case = CreateSport(self.repository)

    def test_create_sport_successfully(self):
        """Crea un deporte cuando el nombre no existe."""
        self.repository.exists_by_name.return_value = False

        sport = self.use_case.execute(name="Fútbol")

        assert sport.name == "Fútbol"
        assert sport.is_active is True
        self.repository.save.assert_called_once()

    def test_create_sport_fails_when_name_exists(self):
        """Lanza excepción si ya existe un deporte con ese nombre."""
        self.repository.exists_by_name.return_value = True

        with pytest.raises(SportAlreadyExistsException):
            self.use_case.execute(name="Fútbol")

        self.repository.save.assert_not_called()
