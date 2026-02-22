from uuid import UUID

from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.value_objects.balance import TotalBalance


class GetTotalBalance:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(self, user_id: UUID) -> TotalBalance:
        # Todas las apuesta del usuario
        bets = self.bet_repository.get_by_user(user_id)

        # Construir mapa de estados
        statuses = self.status_repository.get_all()
        status_map = {s.id: s for s in statuses}

        # Calcular
        calculator = BalanceCalculator(status_map)
        result = calculator.calculate(bets)

        return TotalBalance(**result)
