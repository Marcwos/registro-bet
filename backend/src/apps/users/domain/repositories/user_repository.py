from abc import ABC, abstractmethod

from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.user_id import UserId


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        """Guarda usuario o actualiza usuario"""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User | None:
        """Obtener usuario por id"""

    @abstractmethod
    def get_by_email(self, email: Email) -> User | None:
        """Obtener usuario por email"""
        pass

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        pass

    @abstractmethod
    def count_all(self) -> int:
        """Contar total de usuarios"""
