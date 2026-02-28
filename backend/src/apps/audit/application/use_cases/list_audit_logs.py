from ...domain.repositories.audit_log_repository import AuditLogRepository


class ListAuditLogs:
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def execute(self, limit: int = 50, offset: int = 0) -> dict:
        items = self.audit_log_repository.get_all(limit=limit, offset=offset)
        total = self.audit_log_repository.count_all()
        return {
            "items": items,
            "total": total,
        }
