from ...domain.entities.sport import Sport
from ...domain.repositories.sport_repository import SportRepository


class ListSports:
    def __init__(self, sport_repository: SportRepository):
        self.sport_repository = sport_repository

    def execute(self) -> list[Sport]:
        return self.sport_repository.get_all()
