from ...domain.entities.audit_log import AuditLog
from ..models.audit_log_model import AuditLogModel


class AuditLogMapper:
    @staticmethod
    def to_domain(model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=model.user_id,
            action=model.action,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            metadata=model.metadata,
            ip_address=model.ip_address or "",
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: AuditLog) -> AuditLogModel:
        return AuditLogModel(
            id=entity.id,
            user_id=entity.user_id,
            action=entity.action,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            metadata=entity.metadata,
            ip_address=entity.ip_address or None,
            created_at=entity.created_at,
        )
