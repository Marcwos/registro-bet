"""
Tests — Use Case: UpdateBetCategory
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.update_bet_category import UpdateBetCategory
from ...domain.entities.bet_category import BetCategory
from ...domain.exceptions import BetCategoryAlreadyExistsException, BetCategoryNotFoundException
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class TestUpdateBetCategory:
    def setup_method(self):
        self.repository = Mock(spec=BetCategoryRepository)
        self.use_case = UpdateBetCategory(self.repository)
        self.category_id = uuid4()
        self.existing = BetCategory(id=self.category_id, name="Simple", description="Apuesta simple")

    def test_update_name_successfully(self):
        """Actualiza el nombre cuando no hay conflicto."""
        self.repository.get_by_id.return_value = self.existing
        self.repository.exists_by_name.return_value = False

        result = self.use_case.execute(category_id=self.category_id, name="Simple Plus")

        assert result.name == "Simple Plus"
        self.repository.save.assert_called_once()

    def test_update_description(self):
        """Actualiza la descripción."""
        self.repository.get_by_id.return_value = self.existing

        result = self.use_case.execute(category_id=self.category_id, description="Nueva descripción")

        assert result.description == "Nueva descripción"
        self.repository.save.assert_called_once()

    def test_update_fails_when_not_found(self):
        """Lanza excepción si la categoría no existe."""
        self.repository.get_by_id.return_value = None

        with pytest.raises(BetCategoryNotFoundException):
            self.use_case.execute(category_id=self.category_id, name="Test")

        self.repository.save.assert_not_called()

    def test_update_fails_when_name_already_exists(self):
        """Lanza excepción si el nuevo nombre ya existe."""
        self.repository.get_by_id.return_value = self.existing
        self.repository.exists_by_name.return_value = True

        with pytest.raises(BetCategoryAlreadyExistsException):
            self.use_case.execute(category_id=self.category_id, name="Combinada")

        self.repository.save.assert_not_called()
