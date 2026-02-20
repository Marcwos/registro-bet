from uuid import uuid4

from ...domain.entities.sport import Sport
from ...domain.exceptions import SportAlreadyExistsException
from ...domain.repositories.sport_repository import SportRepository


class CreateSport:
    def __init__(self, sport_repository: SportRepository):
        self.sport_repository = sport_repository

    def execute(self, name: str) -> Sport:
        if self.sport_repository.exists_by_name(name):
            raise SportAlreadyExistsException()

        sport = Sport(id=uuid4(), name=name.strip(), is_active=True)

        self.sport_repository.save(sport)
        return sport
