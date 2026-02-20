from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.bet_status import BetStatus


class BetStatusRepository(ABC):
    @abstractmethod
    def save(self, status: BetStatus) -> None:
        """Guarda o actualiza un estado"""

    @abstractmethod
    def get_by_id(self, status_id: UUID) -> BetStatus | None:
        """Obtener estado por id"""

    @abstractmethod
    def get_by_code(self, code: str) -> BetStatus | None:
        """Obtener estado por codigo"""

    @abstractmethod
    def get_all(self) -> list[BetStatus]:
        """Obtener todos los estados"""

    @abstractmethod
    def exists_by_code(self, code: str) -> bool:
        """Verificar si existe un estado con ese codigo"""
