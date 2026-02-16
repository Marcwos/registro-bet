"""
Tests unitarios para LogoutUser use case.

LogoutUser tiene una lógica simple:
  1. Decodificar el refresh token para obtener session_id
  2. Buscar la sesión en BD
  3. Revocarla

Probamos: logout exitoso, token inválido, sesión no encontrada.
"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.logout_user import LogoutUser
from ...domain.entities.auth_session import AuthSession
from ...domain.exceptions import InvalidTokenException
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.services.token_provider import TokenProvider


class TestLogoutUser:
    def setup_method(self):
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.token_provider = Mock(spec=TokenProvider)

        self.use_case = LogoutUser(
            session_repository=self.session_repo,
            token_provider=self.token_provider,
        )

        self.test_session_id = uuid4()
        self.test_session = AuthSession(
            id=self.test_session_id,
            user_id=uuid4(),
            refresh_token_hash="some_hash",
            expires_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            revoked_at=None,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_logout_successfully(self):
        """
        Escenario: Logout exitoso. La sesión existe y se revoca.
        """
        # ARRANGE
        # decode_refresh_token devuelve el payload con el session_id
        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = self.test_session

        # ACT
        # LogoutUser.execute() no retorna nada (retorna None)
        self.use_case.execute(refresh_token="fake_refresh_token")

        # ASSERT
        # Verificar que se decodificó el token
        self.token_provider.decode_refresh_token.assert_called_once_with("fake_refresh_token")
        # Verificar que se buscó la sesión
        self.session_repo.get_by_id.assert_called_once_with(self.test_session_id)
        # Verificar que se revocó
        self.session_repo.revoke_by_id.assert_called_once_with(self.test_session_id)

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_logout_fails_when_token_is_invalid(self):
        """
        Escenario: El token no se puede decodificar (expirado, corrupto, etc.)
        Resultado: La excepción del token_provider se propaga.
        """
        # ARRANGE
        # side_effect hace que el mock LANCE una excepción en vez de devolver algo
        self.token_provider.decode_refresh_token.side_effect = InvalidTokenException()

        # ACT + ASSERT
        with pytest.raises(InvalidTokenException):
            self.use_case.execute(refresh_token="token_corrupto")

        # No se debe buscar ni revocar nada
        self.session_repo.get_by_id.assert_not_called()
        self.session_repo.revoke_by_id.assert_not_called()

    def test_logout_fails_when_session_not_found(self):
        """
        Escenario: El token es válido, pero la sesión no existe en BD.
        Resultado: InvalidTokenException.
        """
        # ARRANGE
        self.token_provider.decode_refresh_token.return_value = {"session_id": str(self.test_session_id)}
        self.session_repo.get_by_id.return_value = None  # ← no existe

        # ACT + ASSERT
        with pytest.raises(InvalidTokenException):
            self.use_case.execute(refresh_token="fake_refresh_token")

        # Se decodificó y se buscó, pero NO se revocó
        self.token_provider.decode_refresh_token.assert_called_once()
        self.session_repo.get_by_id.assert_called_once()
        self.session_repo.revoke_by_id.assert_not_called()
