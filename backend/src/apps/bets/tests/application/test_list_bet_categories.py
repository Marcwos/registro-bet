"""
Tests — Use Case: ListBetCategories
"""

from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.list_bet_categories import ListBetCategories
from ...domain.entities.bet_category import BetCategory
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class TestListBetCategories:
    def setup_method(self):
        self.repository = Mock(spec=BetCategoryRepository)
        self.use_case = ListBetCategories(self.repository)

    def test_list_categories_returns_all(self):
        """Retorna todas las categorías."""
        categories = [
            BetCategory(id=uuid4(), name="Simple", description="Apuesta simple"),
            BetCategory(id=uuid4(), name="Combinada de 2", description=""),
        ]
        self.repository.get_all.return_value = categories

        result = self.use_case.execute()

        assert len(result) == 2
        self.repository.get_all.assert_called_once()

    def test_list_categories_returns_empty(self):
        """Retorna lista vacía si no hay categorías."""
        self.repository.get_all.return_value = []

        result = self.use_case.execute()

        assert result == []
