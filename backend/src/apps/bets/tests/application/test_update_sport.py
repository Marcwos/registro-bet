"""
Tests — Use Case: UpdateSport

Testeamos:
  - Actualizar nombre exitosamente
  - Actualizar is_active
  - Falla si no existe el deporte
  - Falla si el nuevo nombre ya existe
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.update_sport import UpdateSport
from ...domain.entities.sport import Sport
from ...domain.exceptions import SportAlreadyExistsException, SportNotFoundException
from ...domain.repositories.sport_repository import SportRepository


class TestUpdateSport:
    def setup_method(self):
        self.repository = Mock(spec=SportRepository)
        self.use_case = UpdateSport(self.repository)
        self.sport_id = uuid4()
        self.existing_sport = Sport(id=self.sport_id, name="Fútbol", is_active=True)

    def test_update_name_successfully(self):
        """Actualiza el nombre cuando no hay conflicto."""
        self.repository.get_by_id.return_value = self.existing_sport
        self.repository.exists_by_name.return_value = False

        result = self.use_case.execute(sport_id=self.sport_id, name="Football")

        assert result.name == "Football"
        self.repository.save.assert_called_once()

    def test_update_is_active(self):
        """Desactiva un deporte."""
        self.repository.get_by_id.return_value = self.existing_sport

        result = self.use_case.execute(sport_id=self.sport_id, is_active=False)

        assert result.is_active is False
        self.repository.save.assert_called_once()

    def test_update_fails_when_sport_not_found(self):
        """Lanza excepción si el deporte no existe."""
        self.repository.get_by_id.return_value = None

        with pytest.raises(SportNotFoundException):
            self.use_case.execute(sport_id=self.sport_id, name="Test")

        self.repository.save.assert_not_called()

    def test_update_fails_when_name_already_exists(self):
        """Lanza excepción si el nuevo nombre ya existe."""
        self.repository.get_by_id.return_value = self.existing_sport
        self.repository.exists_by_name.return_value = True

        with pytest.raises(SportAlreadyExistsException):
            self.use_case.execute(sport_id=self.sport_id, name="Tenis")

        self.repository.save.assert_not_called()
