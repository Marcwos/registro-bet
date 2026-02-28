from datetime import UTC, datetime
from uuid import uuid4

from ...domain.entities.audit_log import AuditLog


class TestAuditLog:
    def test_create_audit_log_with_all_fields(self):
        log_id = uuid4()
        user_id = uuid4()
        entity_id = uuid4()

        audit_log = AuditLog(
            id=log_id,
            user_id=user_id,
            action="user_registered",
            entity_type="user",
            entity_id=entity_id,
            metadata={"email": "test@test.com"},
            ip_address="127.0.0.1",
            created_at=datetime.now(UTC),
        )

        assert audit_log.id == log_id
        assert audit_log.user_id == user_id
        assert audit_log.action == "user_registered"
        assert audit_log.entity_type == "user"
        assert audit_log.entity_id == entity_id
        assert audit_log.metadata == {"email": "test@test.com"}
        assert audit_log.ip_address == "127.0.0.1"

    def test_create_audit_log_without_entity_id(self):
        audit_log = AuditLog(
            id=uuid4(),
            user_id=uuid4(),
            action="password_changed",
            entity_type="user",
            entity_id=None,
            metadata={},
            ip_address="",
            created_at=datetime.now(UTC),
        )

        assert audit_log.entity_id is None
        assert audit_log.metadata == {}
        assert audit_log.ip_address == ""

    def test_create_audit_log_with_empty_metadata(self):
        audit_log = AuditLog(
            id=uuid4(),
            user_id=uuid4(),
            action="bet_deleted",
            entity_type="bet",
            entity_id=uuid4(),
            metadata={},
            ip_address="192.168.1.1",
            created_at=datetime.now(UTC),
        )

        assert audit_log.action == "bet_deleted"
        assert audit_log.entity_type == "bet"
        assert audit_log.metadata == {}
