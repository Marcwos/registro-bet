from uuid import UUID

from ...domain.exceptions import BetAccessDeniedException, BetNotFoundException
from ...domain.repositories.bet_repository import BetRepository


class DeleteBet:
    def __init__(self, bet_repository: BetRepository):
        self.bet_repository = bet_repository

    def execute(self, bet_id: UUID, user_id: UUID) -> None:
        bet = self.bet_repository.get_by_id(bet_id)
        if bet is None:
            raise BetNotFoundException()

        if bet.user_id != user_id:
            raise BetAccessDeniedException

        self.bet_repository.delete(bet_id)
