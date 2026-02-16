"""
Tests de dominio — Entidad: AuthSession

Testeamos la estructura del dataclass AuthSession.
"""

from datetime import datetime, timezone, timedelta
from uuid import uuid4

from ...domain.entities.auth_session import AuthSession


class TestAuthSession:

    def test_create_active_session(self):
        """Una sesión activa tiene revoked_at=None."""
        session = AuthSession(
            id=uuid4(),
            user_id=uuid4(),
            refresh_token_hash="some_hash_value",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            user_agent="Mozilla/5.0",
            ip_address="192.168.1.1",
        )

        assert session.revoked_at is None
        assert session.refresh_token_hash == "some_hash_value"

    def test_create_revoked_session(self):
        """Una sesión revocada tiene revoked_at con fecha."""
        now = datetime.now(timezone.utc)
        session = AuthSession(
            id=uuid4(),
            user_id=uuid4(),
            refresh_token_hash="hash",
            expires_at=now + timedelta(days=7),
            created_at=now,
            revoked_at=now,
            user_agent="",
            ip_address="",
        )

        assert session.revoked_at is not None
        assert session.revoked_at == now

    def test_session_stores_user_agent_and_ip(self):
        """La sesión guarda metadata del cliente (user_agent, ip)."""
        session = AuthSession(
            id=uuid4(),
            user_id=uuid4(),
            refresh_token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            user_agent="Chrome/120.0",
            ip_address="10.0.0.1",
        )

        assert session.user_agent == "Chrome/120.0"
        assert session.ip_address == "10.0.0.1"
