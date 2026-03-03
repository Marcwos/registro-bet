from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from ...domain.entities.bet import Bet
from ...domain.exceptions import (
    BetStatusNotFoundException,
    InvalidBetTypeException,
    InvalidOddsException,
    InvalidProfitExpectedException,
    InvalidStakeAmountException,
)
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.tz_utils import get_day_utc_range
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
        title: str = "",
        is_freebet: bool = False,
        is_boosted: bool = False,
        tz_name: str | None = None,
        tz_offset_minutes: int = 0,
    ) -> Bet:
        # Validar exclusividad mutua bono/bonificacion
        if is_freebet and is_boosted:
            raise InvalidBetTypeException()

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

        # Titulo Automatico: "Apuesta N" (timezone-aware)
        if tz_name or tz_offset_minutes != 0:
            # Convertir placed_at a fecha local del usuario
            local_tz = ZoneInfo(tz_name) if tz_name else timezone(timedelta(minutes=-tz_offset_minutes))
            local_date = bet_placed_at.astimezone(local_tz).date()
            utc_start, utc_end = get_day_utc_range(local_date, tz_name=tz_name, tz_offset_minutes=tz_offset_minutes)
            count = self.bet_repository.count_by_user_and_datetime_range(user_id, utc_start, utc_end)
        else:
            local_date = bet_placed_at.date()
            count = self.bet_repository.count_by_user_and_date(user_id, local_date)

        # Priorizar titulo del usuario; fallback a auto-generado
        title = title.strip() if title and title.strip() else f"Apuesta {count + 1}"

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
            is_freebet=is_freebet,
            is_boosted=is_boosted,
            placed_at=bet_placed_at,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

        self.bet_repository.save(bet)
        return bet
