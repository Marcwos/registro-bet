from abc import ABC, abstractmethod
from uuid import UUID


class AuditService(ABC):
    @abstractmethod
    def log(
        self,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        metadata: dict | None = None,
        ip_address: str = "",
    ) -> None:
        """Registra un evento de auditoria"""
