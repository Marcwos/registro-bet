from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.sport import Sport


class SportRepository(ABC):
    @abstractmethod
    def save(self, sport: Sport) -> None:
        """Guarda o actualiza un deporte"""

    @abstractmethod
    def get_by_id(self, sport_id: UUID) -> Sport | None:
        """Obtener deporte por id"""

    @abstractmethod
    def get_all(self) -> list[Sport]:
        """Obtener todos los deportes"""

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """Verifcar si existe un deporte con ese nombre"""
