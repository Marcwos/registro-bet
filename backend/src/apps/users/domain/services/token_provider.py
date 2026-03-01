from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any
from uuid import UUID


class TokenProvider(ABC):
    @abstractmethod
    def generate_access_token(self, user_id: UUID, role: str, email: str = "") -> str:
        """Genera un access token de vida corta"""

    @abstractmethod
    def generate_refresh_token(self, session_id: UUID, lifetime: timedelta | None = None) -> str:
        """Genera un refesh token de vida larga"""

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decodifica y valida un access token. Lanza excepcion si es invalido"""

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        """Decodifica y valida un refesh token. Lanza exception si es invalido"""
