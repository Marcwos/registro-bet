from datetime import UTC, date, datetime, timedelta, timezone
from uuid import UUID

from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.value_objects.balance import DailyBalance


class GetDailyBalance:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(self, user_id: UUID, tarjet_date: date, tz_offset_minutes: int = 0) -> DailyBalance:
        if tz_offset_minutes != 0:
            # Calcular inicio/fin del dia local en UTC
            tz = timezone(timedelta(minutes=-tz_offset_minutes))
            local_start = datetime(tarjet_date.year, tarjet_date.month, tarjet_date.day, tzinfo=tz)
            local_end = local_start + timedelta(days=1)
            utc_start = local_start.astimezone(UTC)
            utc_end = local_end.astimezone(UTC)
            bets = self.bet_repository.get_by_user_and_datetime_range(user_id, utc_start, utc_end)
        else:
            # Sin offset: filtrar por fecha UTC (comportamiento original)
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
