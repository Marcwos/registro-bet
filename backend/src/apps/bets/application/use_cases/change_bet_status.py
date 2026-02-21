from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.exceptions import BetAccessDeniedException, BetNotFoundException, BetStatusNotFoundException
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository


class ChangeStatus:
    def __init__(self, bet_repository: BetRepository, status_repository: BetStatusRepository):
        self.bet_repository = bet_repository
        self.status_repository = status_repository

    def execute(self, bet_id: UUID, user_id: UUID, status_code: str, profit_final: Decimal | None = None) -> Bet:
        bet = self.bet_repository.get_by_id(bet_id)
        if bet is None:
            raise BetNotFoundException()

        if bet.user_id != user_id:
            raise BetAccessDeniedException()

        new_status = self.status_repository.get_by_code(status_code)
        if new_status is None:
            raise BetStatusNotFoundException()

        now = datetime.now(UTC)

        bet.status_id = new_status.id

        # Si el nuevo estado es final -> marcar settled_at
        # Si vuelve a pendiente -> limpiar settled_at
        if new_status.is_final:
            bet.settled_at = now
        else:
            bet.settled_at = None

        # Permitir actualizar la ganancia real justo con el cambio de estado
        if profit_final is not None:
            bet.profit_final = profit_final

        bet.updated_at = now
        self.bet_repository.save(bet)
        return bet
