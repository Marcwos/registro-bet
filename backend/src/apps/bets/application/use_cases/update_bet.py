from datetime import UTC, datetime
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.exceptions import (
    BetAccessDeniedException,
    BetNotEditableException,
    BetNotFoundException,
    InvalidOddsException,
    InvalidStakeAmountException,
)
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class UpdateBet:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(self, bet_id: UUID, user_id: UUID, confirm: bool = False, **updates) -> Bet:
        bet = self.bet_repository.get_by_id(bet_id)
        if bet is None:
            raise BetNotFoundException()

        if bet.user_id != user_id:
            raise BetAccessDeniedException()

        # Solo pendientes pueden editarse libremente; cerradas requieren confirm
        status = self.status_repository.get_by_id(bet.status_id)
        if status and status.is_final and not confirm:
            raise BetNotEditableException()

        # Aplicar actualizaciones
        if "stake_amount" in updates:
            try:
                money = Money(amount=updates["stake_amount"])
            except ValueError as e:
                raise InvalidStakeAmountException(str(e)) from e
            bet.stake_amount = money

        if "odds" in updates:
            try:
                bet_odds = Odds(value=updates["odds"])
            except ValueError as e:
                raise InvalidOddsException(str(e)) from e
            bet.odds = bet_odds

        if "profit_expected" in updates:
            bet.profit_expected = updates["profit_expected"]

        if "profit_final" in updates:
            bet.profit_final = updates["profit_final"]

        if "placed_at" in updates:
            bet.placed_at = updates["placed_at"]

        if "description" in updates:
            bet.description = updates["description"].strip()

        bet.updated_at = datetime.now(UTC)
        self.bet_repository.save(bet)
        return bet
