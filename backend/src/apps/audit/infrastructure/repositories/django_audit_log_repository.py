from ...domain.entities.audit_log import AuditLog
from ...domain.repositories.audit_log_repository import AuditLogRepository
from ..mappers.audit_log_mapper import AuditLogMapper
from ..models.audit_log_model import AuditLogModel


class DjangoAuditLogRepository(AuditLogRepository):
    def save(self, audit_log: AuditLog) -> None:
        model = AuditLogMapper.to_model(audit_log)
        model.save()

    def get_all(self, limit: int = 50, offset: int = 0) -> list[AuditLog]:
        models = AuditLogModel.objects.all()[offset : offset + limit]
        return [AuditLogMapper.to_domain(m) for m in models]

    def count_all(self) -> int:
        return AuditLogModel.objects.count()
