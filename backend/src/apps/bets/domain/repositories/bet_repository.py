from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from ..entities.bet import Bet


class BetRepository(ABC):
    @abstractmethod
    def save(self, bet: Bet) -> None:
        """Guarda o actualiza una apuesta"""

    @abstractmethod
    def get_by_id(self, bet_id: UUID) -> Bet | None:
        """Obtener apuesta por id"""

    @abstractmethod
    def get_by_user(self, bet_id: UUID) -> list[Bet]:
        """Obtener todas las apuestas de un usuario"""

    @abstractmethod
    def delete(self, bet_id: UUID) -> None:
        """Eliminar una apuesta"""

    @abstractmethod
    def count_by_user_and_date(self, user_id: UUID, tarjet_date: date) -> int:
        """Contar apuestas de un usuario en una fecha (para titulo automatico)"""

    @abstractmethod
    def get_by_user_and_date(self, user_id: UUID, tarjet_date: date) -> list[Bet]:
        """Obtener apuestas de un usuario en una fecha especifica"""

    @abstractmethod
    def get_by_user_date_range(self, user_id: UUID, start_date: date, end_date: date) -> list[Bet]:
        """Obtener apuestas de un usuario en un rango de fechas"""
