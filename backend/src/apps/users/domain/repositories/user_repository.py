from abc import ABC, abstractmethod
from typing import Optional

from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.user_id import UserId

class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> None:
        """Guarda usuario o actualiza usuario"""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Obtener usuario por id"""

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """Obtener usuario por email"""
        pass

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        pass