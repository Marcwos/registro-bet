from datetime import date
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.repositories.bet_repository import BetRepository
from ..mappers.bet_mapper import BetMapper
from ..models.bet_model import BetModel


class DjangoBetRepository(BetRepository):
    def save(self, bet: Bet) -> None:
        model = BetMapper.to_model(bet)
        if BetModel.objects.filter(id=bet.id).exists():
            model._state.adding = False
            model.save(
                update_fields=[
                    "title",
                    "stake_amount",
                    "odds",
                    "profit_expected",
                    "profit_final",
                    "status_id",
                    "sport_id",
                    "category_id",
                    "description",
                    "placed_at",
                    "settled_at",
                    "updated_at",
                ]
            )
        else:
            model.save()

    def get_by_id(self, bet_id: UUID) -> Bet | None:
        try:
            model = BetModel.objects.get(id=bet_id)
            return BetMapper.to_domain(model)
        except BetModel.DoesNotExist:
            return None

    def get_by_user(self, user_id: UUID) -> list[Bet]:
        models = BetModel.objects.filter(user_id=user_id).order_by("-placed_at")
        return [BetMapper.to_domain(m) for m in models]

    def delete(self, bet_id: UUID) -> None:
        BetModel.objects.filter(id=bet_id).delete()

    def count_by_user_and_date(self, user_id: UUID, target_date: date) -> int:
        return BetModel.objects.filter(
            user_id=user_id,
            placed_at__date=target_date,
        ).count()
