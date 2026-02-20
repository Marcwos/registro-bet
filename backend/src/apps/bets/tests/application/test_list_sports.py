"""
Tests — Use Case: ListSports

Testeamos:
  - Retorna lista de deportes
  - Retorna lista vacía si no hay deportes
"""

from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.list_sports import ListSports
from ...domain.entities.sport import Sport
from ...domain.repositories.sport_repository import SportRepository


class TestListSports:
    def setup_method(self):
        self.repository = Mock(spec=SportRepository)
        self.use_case = ListSports(self.repository)

    def test_list_sports_returns_all(self):
        """Retorna todos los deportes del repositorio."""
        sports = [
            Sport(id=uuid4(), name="Fútbol", is_active=True),
            Sport(id=uuid4(), name="Tenis", is_active=True),
        ]
        self.repository.get_all.return_value = sports

        result = self.use_case.execute()

        assert len(result) == 2
        self.repository.get_all.assert_called_once()

    def test_list_sports_returns_empty(self):
        """Retorna lista vacía si no hay deportes."""
        self.repository.get_all.return_value = []

        result = self.use_case.execute()

        assert result == []
