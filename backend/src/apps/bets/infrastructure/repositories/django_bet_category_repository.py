from uuid import UUID

from ...domain.entities.bet_category import BetCategory
from ...domain.repositories.bet_category_repository import BetCategoryRepository
from ..mappers.bet_category_mapper import BetCategoryMapper
from ..models.bet_category_model import BetCategoryModel


class DjangoBetCategoryRepository(BetCategoryRepository):
    def save(self, category: BetCategory) -> None:
        model = BetCategoryMapper.to_model(category)
        if BetCategoryModel.objects.filter(id=category.id).exists():
            model._state.adding = False
            model.save(update_fields=["name", "description"])
        else:
            model.save()

    def get_by_id(self, category_id: UUID) -> BetCategory | None:
        try:
            model = BetCategoryModel.objects.get(id=category_id)
            return BetCategoryMapper.to_domain(model)
        except BetCategoryModel.DoesNotExist:
            return None

    def get_all(self) -> list[BetCategory]:
        models = BetCategoryModel.objects.all().order_by("name")
        return [BetCategoryMapper.to_domain(m) for m in models]

    def exists_by_name(self, name: str) -> bool:
        return BetCategoryModel.objects.filter(name__iexact=name).exists()
