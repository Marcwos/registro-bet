"""
Tests unitarios para RefreshToken use case.

RefreshToken es el caso de uso más complejo porque tiene más pasos:
  1. Decodificar refresh token
  2. Buscar sesión en BD
  3. Verificar que no esté revocada
  4. Verificar hash del token
  5. Verificar que no haya expirado
  6. Buscar usuario
  7. Revocar sesión vieja + crear nueva (rotación)
  8. Generar nuevo access token

Cada paso que puede fallar = un test de error.
"""

import hashlib
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.refresh_token import RefreshResult, RefreshToken
from ...domain.entities.auth_session import AuthSession
from ...domain.entities.user import User
from ...domain.exceptions import (
    InvalidTokenException,
    SessionRevokedException,
    UserNotFoundException,
)
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.token_provider import TokenProvider
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestRefreshToken:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.token_provider = Mock(spec=TokenProvider)

        self.use_case = RefreshToken(
            user_repository=self.user_repo,
            session_repository=self.session_repo,
            token_provider=self.token_provider,
        )

        # Datos reutilizables
        self.test_user_id = uuid4()
        self.test_session_id = uuid4()
        self.raw_refresh_token = "fake_refresh_token_123"
        self.token_hash = hashlib.sha256(self.raw_refresh_token.encode()).hexdigest()

        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.test_session = AuthSession(
            id=self.test_session_id,
            user_id=self.test_user_id,
            refresh_token_hash=self.token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=7),  # No expirada
            created_at=datetime.now(UTC),
            revoked_at=None,  # No revocada
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_refresh_token_successfully(self):
        """
        Escenario: Refresh exitoso. Se rota el token y se crea nueva sesión.
        """
        # ARRANGE
        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = self.test_session
        self.user_repo.get_by_id.return_value = self.test_user
        self.token_provider.generate_refresh_token.return_value = "new_refresh_token"
        self.token_provider.generate_access_token.return_value = "new_access_token"

        # ACT
        result = self.use_case.execute(refresh_token=self.raw_refresh_token)

        # ASSERT
        assert isinstance(result, RefreshResult)

        # Verificar que se revocó la sesión vieja
        self.session_repo.revoke_by_id.assert_called_once_with(self.test_session_id)
        # Verificar que se guardó una nueva sesión
        self.session_repo.save.assert_called_once()
        # Verificar que se generó un nuevo access token
        self.token_provider.generate_access_token.assert_called_once()

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_refresh_fails_when_token_invalid(self):
        """Token no se puede decodificar."""
        self.token_provider.decode_refresh_token.side_effect = InvalidTokenException()

        with pytest.raises(InvalidTokenException):
            self.use_case.execute(refresh_token="corrupted_token")

    def test_refresh_fails_when_session_not_found(self):
        """El session_id del token no existe en BD."""
        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = None

        with pytest.raises(InvalidTokenException):
            self.use_case.execute(refresh_token=self.raw_refresh_token)

    def test_refresh_fails_when_session_is_revoked(self):
        """La sesión ya fue revocada (logout previo)."""
        revoked_session = AuthSession(
            id=self.test_session_id,
            user_id=self.test_user_id,
            refresh_token_hash=self.token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
            revoked_at=datetime.now(UTC),  # ← YA REVOCADA
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = revoked_session

        with pytest.raises(SessionRevokedException):
            self.use_case.execute(refresh_token=self.raw_refresh_token)

        # No se debe crear nueva sesión si la vieja estaba revocada
        self.session_repo.save.assert_not_called()

    def test_refresh_fails_when_token_hash_does_not_match(self):
        """El hash del token no coincide con el guardado en la sesión."""
        tampered_session = AuthSession(
            id=self.test_session_id,
            user_id=self.test_user_id,
            refresh_token_hash="hash_diferente_al_del_token",  # ← No coincide
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
            revoked_at=None,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = tampered_session

        with pytest.raises(InvalidTokenException):
            self.use_case.execute(refresh_token=self.raw_refresh_token)

    def test_refresh_fails_when_session_is_expired(self):
        """La sesión expiró (más de 7 días)."""
        expired_session = AuthSession(
            id=self.test_session_id,
            user_id=self.test_user_id,
            refresh_token_hash=self.token_hash,
            expires_at=datetime.now(UTC) - timedelta(days=1),  # ← EXPIRADA
            created_at=datetime.now(UTC) - timedelta(days=8),
            revoked_at=None,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = expired_session

        with pytest.raises(UserNotFoundException):
            self.use_case.execute(refresh_token=self.raw_refresh_token)

    def test_refresh_fails_when_user_not_found(self):
        """El usuario de la sesión ya no existe."""
        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = self.test_session
        self.user_repo.get_by_id.return_value = None  # ← usuario eliminado

        with pytest.raises(UserNotFoundException):
            self.use_case.execute(refresh_token=self.raw_refresh_token)
