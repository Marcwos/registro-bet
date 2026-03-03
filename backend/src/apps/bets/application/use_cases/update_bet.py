from datetime import UTC, datetime
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.exceptions import (
    BetAccessDeniedException,
    BetNotEditableException,
    BetNotFoundException,
    InvalidBetTypeException,
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

        self._apply_updates(bet, updates)

        # Validar exclusividad mutua bono/bonificacion
        if bet.is_freebet and bet.is_boosted:
            raise InvalidBetTypeException()

        bet.updated_at = datetime.now(UTC)
        self.bet_repository.save(bet)
        return bet

    def _apply_updates(self, bet: Bet, updates: dict) -> None:
        """Aplica las actualizaciones al dominio validando value objects."""
        if "stake_amount" in updates:
            try:
                bet.stake_amount = Money(amount=updates["stake_amount"])
            except ValueError as e:
                raise InvalidStakeAmountException(str(e)) from e

        if "odds" in updates:
            try:
                bet.odds = Odds(value=updates["odds"])
            except ValueError as e:
                raise InvalidOddsException(str(e)) from e

        # Campos simples sin validacion de VO
        simple_fields = ("profit_expected", "profit_final", "placed_at", "is_freebet", "is_boosted")
        for field in simple_fields:
            if field in updates:
                setattr(bet, field, updates[field])

        if "description" in updates:
            bet.description = updates["description"].strip()

        if "title" in updates:
            new_title = updates["title"].strip()
            if new_title:
                bet.title = new_title
        return bet
