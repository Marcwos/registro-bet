from abc import ABC, abstractmethod

class PasswordHasher(ABC):

    @abstractmethod
    def hash(self, password: str) -> str:
        """Convierte un password plano en hash seguro"""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verifica si un password plano coincide con el hash"""