from datetime import date
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.value_objects.balance import BetHistorySummay


class GetBetHistory:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(self, user_id: UUID, start_date: date, end_date: date) -> tuple[list[Bet], BetHistorySummay]:
        """Retorna:
        - Lista de apuestas en el juego
        - Resumen (totales) del rango"""
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
