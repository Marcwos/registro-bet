from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.log_event import LogEvent
from ...domain.repositories.audit_log_repository import AuditLogRepository


class TestLogEvent:
    def setup_method(self):
        self.repository = Mock(spec=AuditLogRepository)
        self.use_case = LogEvent(self.repository)

    def test_log_event_saves_audit_log(self):
        user_id = uuid4()
        entity_id = uuid4()

        result = self.use_case.execute(
            user_id=user_id,
            action="user_registered",
            entity_type="user",
            entity_id=entity_id,
            metadata={"email": "test@test.com"},
            ip_address="127.0.0.1",
        )

        assert result.user_id == user_id
        assert result.action == "user_registered"
        assert result.entity_type == "user"
        assert result.entity_id == entity_id
        assert result.metadata == {"email": "test@test.com"}
        assert result.ip_address == "127.0.0.1"
        self.repository.save.assert_called_once()

    def test_log_event_with_default_metadata(self):
        user_id = uuid4()

        result = self.use_case.execute(
            user_id=user_id,
            action="user_logged_in",
            entity_type="user",
        )

        assert result.metadata == {}
        assert result.ip_address == ""
        self.repository.save.assert_called_once()

    def test_log_event_without_entity_id(self):
        user_id = uuid4()

        result = self.use_case.execute(
            user_id=user_id,
            action="password_changed",
            entity_type="user",
            entity_id=None,
        )

        assert result.entity_id is None
        self.repository.save.assert_called_once()
