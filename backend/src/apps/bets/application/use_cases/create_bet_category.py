from uuid import uuid4

from ...domain.entities.bet_category import BetCategory
from ...domain.exceptions import BetCategoryAlreadyExistsException
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class CreateBetCategory:
    def __init__(self, category_repository: BetCategoryRepository):
        self.category_repository = category_repository

    def execute(self, name: str, description: str = "") -> BetCategory:
        if self.category_repository.exists_by_name(name):
            raise BetCategoryAlreadyExistsException()

        category = BetCategory(id=uuid4(), name=name.strip(), description=description.strip())

        self.category_repository.save(category)
        return category
