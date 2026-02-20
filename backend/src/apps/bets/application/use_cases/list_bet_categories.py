from ...domain.entities.bet_category import BetCategory
from ...domain.repositories.bet_category_repository import BetCategoryRepository


class ListBetCategories:
    def __init__(self, category_repository: BetCategoryRepository):
        self.category_repository = category_repository

    def execute(self) -> list[BetCategory]:
        return self.category_repository.get_all()
