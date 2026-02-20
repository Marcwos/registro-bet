from uuid import UUID

from ...domain.entities.sport import Sport
from ...domain.repositories.sport_repository import SportRepository
from ..mappers.sport_mapper import SportMapper
from ..models.sport_model import SportModel


class DjangoSportRepository(SportRepository):
    def save(self, sport: Sport) -> None:
        model = SportMapper.to_model(sport)
        if SportModel.objects.filter(id=sport.id).exists():
            model._state.adding = False
            model.save(update_fields=["name", "is_active"])
        else:
            model.save()

    def get_by_id(self, sport_id: UUID) -> Sport | None:
        try:
            model = SportModel.objects.get(id=sport_id)
            return SportMapper.to_domain(model)
        except SportModel.DoesNotExist:
            return None

    def get_all(self) -> list[Sport]:
        models = SportModel.objects.all().order_by("name")
        return [SportMapper.to_domain(m) for m in models]

    def exists_by_name(self, name: str) -> bool:
        return SportModel.objects.filter(name__iexact=name).exists()
