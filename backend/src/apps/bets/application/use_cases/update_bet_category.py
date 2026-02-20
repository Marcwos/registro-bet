from uuid import UUID

from ...domain.entities.bet_category import BetCategory
from ...domain.exceptions import BetCategoryAlreadyExistsException, BetCategoryNotFoundException
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class UpdateBetCategory:
    def __init__(self, category_repository: BetCategoryRepository):
        self.category_repository = category_repository

    def execute(self, category_id: UUID, name: str | None = None, description: str | None = None) -> BetCategory:
        category = self.category_repository.get_by_id(category_id)
        if category is None:
            raise BetCategoryNotFoundException()

        if name is not None and name.strip().lower() != category.name.lower():
            if self.category_repository.exists_by_name(name):
                raise BetCategoryAlreadyExistsException()
            category.name = name.strip()

        if description is not None:
            category.description = description.strip()

        self.category_repository.save(category)
        return category
