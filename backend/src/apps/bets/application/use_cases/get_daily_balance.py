from datetime import date
from uuid import UUID

from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.services.tz_utils import get_day_utc_range
from ...domain.value_objects.balance import DailyBalance


class GetDailyBalance:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(
        self,
        user_id: UUID,
        tarjet_date: date,
        tz_name: str | None = None,
        tz_offset_minutes: int = 0,
    ) -> DailyBalance:
        if tz_name or tz_offset_minutes != 0:
            utc_start, utc_end = get_day_utc_range(tarjet_date, tz_name=tz_name, tz_offset_minutes=tz_offset_minutes)
            bets = self.bet_repository.get_by_user_and_datetime_range(user_id, utc_start, utc_end)
        else:
            bets = self.bet_repository.get_by_user_and_date(user_id, tarjet_date)

        # Construir mapa de estados para el calculador
        statuses = self.status_repository.get_all()
        status_map = {s.id: s for s in statuses}

        # Calcular desde datos reales
        calculator = BalanceCalculator(status_map)
        result = calculator.calculate(bets)

        return DailyBalance(
            tarjet_date=tarjet_date,
            **result,
        )
