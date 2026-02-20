from ...domain.entities.bet_status import BetStatus
from ...domain.repositories.bet_status_repository import BetStatusRepository


class ListBetStatuses:
    def __init__(self, status_repository: BetStatusRepository):
        self.status_repository = status_repository

    def execute(self) -> list[BetStatus]:
        return self.status_repository.get_all()
