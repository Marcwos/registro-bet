from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.list_audit_logs import ListAuditLogs
from ...domain.entities.audit_log import AuditLog
from ...domain.repositories.audit_log_repository import AuditLogRepository


def _make_audit_log(**overrides) -> AuditLog:
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "action": "user_registered",
        "entity_type": "user",
        "entity_id": uuid4(),
        "metadata": {},
        "ip_address": "127.0.0.1",
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return AuditLog(**defaults)


class TestListAuditLogs:
    def setup_method(self):
        self.repository = Mock(spec=AuditLogRepository)
        self.use_case = ListAuditLogs(self.repository)

    def test_list_audit_logs_returns_items_and_total(self):
        logs = [_make_audit_log(), _make_audit_log(), _make_audit_log()]
        self.repository.get_all.return_value = logs
        self.repository.count_all.return_value = 3

        result = self.use_case.execute(limit=50, offset=0)

        assert len(result["items"]) == 3
        assert result["total"] == 3
        self.repository.get_all.assert_called_once_with(limit=50, offset=0)
        self.repository.count_all.assert_called_once()

    def test_list_audit_logs_with_pagination(self):
        logs = [_make_audit_log()]
        self.repository.get_all.return_value = logs
        self.repository.count_all.return_value = 100

        result = self.use_case.execute(limit=10, offset=90)

        assert len(result["items"]) == 1
        assert result["total"] == 100
        self.repository.get_all.assert_called_once_with(limit=10, offset=90)

    def test_list_audit_logs_empty(self):
        self.repository.get_all.return_value = []
        self.repository.count_all.return_value = 0

        result = self.use_case.execute()

        assert result["items"] == []
        assert result["total"] == 0

    def test_list_audit_logs_default_params(self):
        self.repository.get_all.return_value = []
        self.repository.count_all.return_value = 0

        self.use_case.execute()

        self.repository.get_all.assert_called_once_with(limit=50, offset=0)
