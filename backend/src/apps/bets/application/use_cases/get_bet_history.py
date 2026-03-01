from datetime import date
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.services.tz_utils import get_day_utc_range
from ...domain.value_objects.balance import BetHistorySummay


class GetBetHistory:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        tz_name: str | None = None,
        tz_offset_minutes: int = 0,
    ) -> tuple[list[Bet], BetHistorySummay]:
        """Retorna:
        - Lista de apuestas en el rango
        - Resumen (totales) del rango"""
        if tz_name or tz_offset_minutes != 0:
            # Inicio del start_date local → UTC
            utc_start, _ = get_day_utc_range(start_date, tz_name=tz_name, tz_offset_minutes=tz_offset_minutes)
            # Fin del end_date local → UTC
            _, utc_end = get_day_utc_range(end_date, tz_name=tz_name, tz_offset_minutes=tz_offset_minutes)
            bets = self.bet_repository.get_by_user_and_datetime_range(user_id, utc_start, utc_end)
        else:
            bets = self.bet_repository.get_by_user_date_range(user_id, start_date, end_date)

        # Construir mapa de estados
        statuses = self.status_repository.get_all()
        status_map = {s.id: s for s in statuses}

        # Calcular resumen
        calculator = BalanceCalculator(status_map)
        result = calculator.calculate(bets)

        summary = BetHistorySummay(
            start_date=start_date,
            end_date=end_date,
            **result,
        )

        return bets, summary
