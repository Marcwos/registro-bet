from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.repositories.bet_repository import BetRepository


class ListUserBets:
    def __init__(self, bet_repository: BetRepository):
        self.bet_repository = bet_repository

    def execute(self, user_id: UUID) -> list[Bet]:
        return self.bet_repository.get_by_user(user_id)
