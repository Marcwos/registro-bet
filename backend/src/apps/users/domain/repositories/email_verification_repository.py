from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.email_verification import EmailVerification


class EmailVerficationRepository(ABC):
    @abstractmethod
    def save(self, verfication: EmailVerification) -> None:
        """Guarda un nuevo codigo de un usuario"""

    @abstractmethod
    def get_latest_by_user(self, user_id: UUID) -> EmailVerification:
        """Obtiene el codigo mas reciente de un usuario"""

    @abstractmethod
    def mark_as_used(self, verification_id: UUID) -> None:
        """Marca el codigo como usado"""

    @abstractmethod
    def increment_attempts(self, verfication_id: UUID) -> None:
        """Incrementa el contado de intentos"""
