from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.bet_category import BetCategory


class BetCategoryRepository(ABC):
    @abstractmethod
    def save(self, category: BetCategory) -> None:
        """Guarda o actualiza una categoria"""

    @abstractmethod
    def get_by_id(self, category_id: UUID) -> BetCategory | None:
        """Obtener catgeoria por id"""

    @abstractmethod
    def get_all(self) -> list[BetCategory]:
        """Obtener todas las categorias"""

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """Verificar si existe una categoria con ese nombre"""
