from abc import ABC, abstractmethod

from ..entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    def save(self, audit_log: AuditLog) -> None:
        """Guarda un evento de auditoria"""

    @abstractmethod
    def get_all(self, limit: int = 50, offset: int = 0) -> list[AuditLog]:
        """Obtener eventos de auditoria paginados"""

    @abstractmethod
    def count_all(self) -> int:
        """Contar total de eventos de auditoria"""
