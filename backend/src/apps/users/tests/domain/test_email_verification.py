"""
Tests de dominio — Entidad: EmailVerification
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from ...domain.entities.email_verification import EmailVerification


class TestEmailVerification:
    def test_create_active_verification(self):
        verification = EmailVerification(
            id=uuid4(),
            user_id=uuid4(),
            code_hash="abc123hash",
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )

        assert verification.code_hash == "abc123hash"
        assert verification.purpose == "email_verification"
        assert verification.used_at is None
        assert verification.attempts == 0

    def test_create_used_verification(self):
        now = datetime.now(UTC)
        verification = EmailVerification(
            id=uuid4(),
            user_id=uuid4(),
            code_hash="hash",
            purpose="email_verification",
            expires_at=now + timedelta(minutes=10),
            created_at=now,
            used_at=now,
            attempts=1,
        )

        assert verification.used_at is not None
        assert verification.used_at == now
        assert verification.attempts == 1

    def test_create_password_recovery_verification(self):
        verification = EmailVerification(
            id=uuid4(),
            user_id=uuid4(),
            code_hash="recovery_hash",
            purpose="password_recovery",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )

        assert verification.purpose == "password_recovery"

    def test_verification_stores_user_id(self):
        user_id = uuid4()
        verification = EmailVerification(
            id=uuid4(),
            user_id=user_id,
            code_hash="hash",
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )

        assert verification.user_id == user_id
