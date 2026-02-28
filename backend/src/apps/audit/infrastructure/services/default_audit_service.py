from datetime import UTC, datetime
from uuid import UUID, uuid4

from ...domain.entities.audit_log import AuditLog
from ...domain.repositories.audit_log_repository import AuditLogRepository
from ...domain.services.audit_service import AuditService


class DefaultAuditService(AuditService):
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def log(
        self,
        user_id: UUID,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        metadata: dict | None = None,
        ip_address: str = "",
    ) -> None:
        audit_log = AuditLog(
            id=uuid4(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
            ip_address=ip_address,
            created_at=datetime.now(UTC),
        )
        self.audit_log_repository.save(audit_log)
