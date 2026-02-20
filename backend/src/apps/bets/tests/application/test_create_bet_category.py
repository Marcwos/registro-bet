"""
Tests — Use Case: CreateBetCategory

Testeamos:
  - Crear categoría exitosamente
  - Crear con descripción vacía
  - Falla si ya existe
"""

from unittest.mock import Mock

import pytest

from ...application.use_cases.create_bet_category import CreateBetCategory
from ...domain.exceptions import BetCategoryAlreadyExistsException
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class TestCreateBetCategory:
    def setup_method(self):
        self.repository = Mock(spec=BetCategoryRepository)
        self.use_case = CreateBetCategory(self.repository)

    def test_create_category_successfully(self):
        """Crea una categoría con nombre y descripción."""
        self.repository.exists_by_name.return_value = False

        category = self.use_case.execute(name="Simple", description="Apuesta simple")

        assert category.name == "Simple"
        assert category.description == "Apuesta simple"
        self.repository.save.assert_called_once()

    def test_create_category_with_empty_description(self):
        """Crea una categoría sin descripción."""
        self.repository.exists_by_name.return_value = False

        category = self.use_case.execute(name="Combinada de 2")

        assert category.name == "Combinada de 2"
        assert category.description == ""
        self.repository.save.assert_called_once()

    def test_create_category_fails_when_name_exists(self):
        """Lanza excepción si ya existe una categoría con ese nombre."""
        self.repository.exists_by_name.return_value = True

        with pytest.raises(BetCategoryAlreadyExistsException):
            self.use_case.execute(name="Simple")

        self.repository.save.assert_not_called()
