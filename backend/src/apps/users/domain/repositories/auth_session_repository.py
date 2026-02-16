from abc import ABC, abstractmethod
from uuid import UUID

from ..entities.auth_session import AuthSession


class AuthSessionRepository(ABC):
    @abstractmethod
    def save(self, session: AuthSession) -> None:
        """Guarda nueva sesión"""

    @abstractmethod
    def get_by_id(self, session_id: UUID) -> AuthSession | None:
        """Obtener sesion por su id"""

    @abstractmethod
    def revoke_by_id(self, session_id: UUID) -> None:
        """Revocar una sesion especifica"""

    @abstractmethod
    def revoke_all_by_user(self, user_id: UUID) -> None:
        """Revocar TODAS las sesiones de un usuario(al cambiar contraseña)"""
