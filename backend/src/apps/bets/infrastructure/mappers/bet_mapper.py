from ...domain.entities.bet import Bet
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds
from ..models.bet_model import BetModel


class BetMapper:
    @staticmethod
    def to_domain(model: BetModel) -> Bet:
        return Bet(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            stake_amount=Money(amount=model.stake_amount),
            odds=Odds(value=model.odds),
            profit_expected=model.profit_expected,
            profit_final=model.profit_final,
            status_id=model.status_id,
            sport_id=model.sport_id,
            category_id=model.category_id,
            description=model.description,
            is_freebet=model.is_freebet,
            is_boosted=model.is_boosted,
            placed_at=model.placed_at,
            settled_at=model.settled_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Bet) -> BetModel:
        return BetModel(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            stake_amount=entity.stake_amount.amount,
            odds=entity.odds.value,
            profit_expected=entity.profit_expected,
            profit_final=entity.profit_final,
            status_id=entity.status_id,
            sport_id=entity.sport_id,
            category_id=entity.category_id,
            description=entity.description,
            is_freebet=entity.is_freebet,
            is_boosted=entity.is_boosted,
            placed_at=entity.placed_at,
            settled_at=entity.settled_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
