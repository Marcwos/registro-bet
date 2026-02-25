from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from ...domain.entities.bet import Bet
from ...domain.exceptions import (
    BetStatusNotFoundException,
    InvalidOddsException,
    InvalidProfitExpectedException,
    InvalidStakeAmountException,
)
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class CreateBet:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(
        self,
        user_id: UUID,
        stake_amount: Decimal,
        odds: Decimal,
        profit_expected: Decimal,
        profit_final: Decimal | None = None,
        placed_at: datetime | None = None,
        sport_id: UUID | None = None,
        category_id: UUID | None = None,
        description: str = "",
    ) -> Bet:
        # Valida monto y couta con value Objects
        try:
            money = Money(amount=stake_amount)
        except ValueError as e:
            raise InvalidStakeAmountException(str(e)) from e

        try:
            bet_odds = Odds(value=odds)
        except ValueError as e:
            raise InvalidOddsException(str(e)) from e

        # Obtener estado pendiente
        pending_status = self.status_repository.get_by_code("pending")
        if pending_status is None:
            raise BetStatusNotFoundException()

        # Fecha de apuesta
        now = datetime.now(UTC)
        bet_placed_at = placed_at or now

        # Validar ganancia esperada
        if profit_expected is None or profit_expected < Decimal("0"):
            raise InvalidProfitExpectedException("La ganancia esperada debe ser mayor o igual a 0.")

        # Titulo Automatico: "Apuesta N"
        bet_date = bet_placed_at.date()
        count = self.bet_repository.count_by_user_and_date(user_id, bet_date)
        title = f"Apuesta {count + 1}"

        bet = Bet(
            id=uuid4(),
            user_id=user_id,
            title=title,
            stake_amount=money,
            odds=bet_odds,
            profit_expected=profit_expected,
            profit_final=profit_final,
            status_id=pending_status.id,
            sport_id=sport_id,
            category_id=category_id,
            description=description.strip(),
            placed_at=bet_placed_at,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

        self.bet_repository.save(bet)
        return bet
