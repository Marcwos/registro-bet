from uuid import UUID

from ...domain.entities.sport import Sport
from ...domain.exceptions import SportAlreadyExistsException, SportNotFoundException
from ...domain.repositories.sport_repository import SportRepository


class UpdateSport:
    def __init__(self, sport_repository: SportRepository):
        self.sport_repository = sport_repository

    def execute(self, sport_id: UUID, name: str | None = None, is_active: bool | None = None) -> Sport:
        sport = self.sport_repository.get_by_id(sport_id)
        if sport is None:
            raise SportNotFoundException()

        if name is not None and name.strip().lower() != sport.name.lower():
            if self.sport_repository.exists_by_name(name):
                raise SportAlreadyExistsException()
            sport.name = name.strip()

        if is_active is not None:
            sport.is_active = is_active

        self.sport_repository.save(sport)
        return sport
