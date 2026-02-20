from ...domain.entities.bet_category import BetCategory
from ..models.bet_category_model import BetCategoryModel


class BetCategoryMapper:
    @staticmethod
    def to_domain(model: BetCategoryModel) -> BetCategory:
        return BetCategory(
            id=model.id,
            name=model.name,
            description=model.description,
        )

    @staticmethod
    def to_model(entity: BetCategory) -> BetCategoryModel:
        return BetCategoryModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )
