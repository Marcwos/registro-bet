from uuid import UUID

from ...domain.entities.bet_status import BetStatus
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ..mappers.bet_status_mapper import BetStatusMapper
from ..models.bet_status_model import BetStatusModel


class DjangoBetStatusRepository(BetStatusRepository):
    def save(self, status: BetStatus) -> None:
        model = BetStatusMapper.to_model(status)
        if BetStatusModel.objects.filter(id=status.id).exists():
            model._state.adding = False
            model.save(update_fields=["name", "code", "is_final"])
        else:
            model.save()

    def get_by_id(self, status_id: UUID) -> BetStatus | None:
        try:
            model = BetStatusModel.objects.get(id=status_id)
            return BetStatusMapper.to_main(model)
        except BetStatusModel.DoesNotExist:
            return None

    def get_by_code(self, code: str) -> BetStatus | None:
        try:
            model = BetStatusModel.objects.get(code=code)
            return BetStatusMapper.to_main(model)
        except BetStatusModel.DoesNotExist:
            return None

    def get_all(self) -> list[BetStatus]:
        models = BetStatusModel.objects.all().order_by("name")
        return [BetStatusMapper.to_main(m) for m in models]

    def exists_by_code(self, code: str) -> bool:
        return BetStatusModel.objects.filter(code=code).exists()
