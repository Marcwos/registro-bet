"""
Tests unitarios para LoginUser use case.

Aquí probamos la lógica de login:
  - Buscar usuario por email
  - Verificar contraseña
  - Crear sesión
  - Generar tokens

Como LoginUser tiene 4 dependencias (user_repo, session_repo, hasher, token_provider),
creamos 4 mocks. Cada mock simula una dependencia.
"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.login_user import LoginResult, LoginUser
from ...domain.entities.user import User
from ...domain.exceptions import InvalidCredentialsException
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.services.token_provider import TokenProvider
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestLoginUser:
    def setup_method(self):
        """Crea mocks frescos para cada test."""
        self.user_repo = Mock(spec=UserRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.password_hasher = Mock(spec=PasswordHasher)
        self.token_provider = Mock(spec=TokenProvider)

        self.use_case = LoginUser(
            user_repository=self.user_repo,
            session_repository=self.session_repo,
            password_hasher=self.password_hasher,
            token_provider=self.token_provider,
        )

        # Datos de prueba reutilizables
        self.test_user_id = uuid4()
        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="hashed_password",
            role=Role.USER,
            is_email_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_login_successfully(self):
        """
        Escenario: Login exitoso con credenciales correctas.
        Resultado: Devuelve LoginResult con access_token, refresh_token, etc.
        """
        # ARRANGE
        self.user_repo.get_by_email.return_value = self.test_user
        self.password_hasher.verify.return_value = True  # ← contraseña correcta
        self.token_provider.generate_access_token.return_value = "fake_access_token"
        self.token_provider.generate_refresh_token.return_value = "fake_refresh_token"

        # ACT
        result = self.use_case.execute(
            email="test@example.com",
            password="correctpassword",
            user_agent="Mozilla/5.0",
            ip_address="192.168.1.1",
        )

        # ASSERT
        assert isinstance(result, LoginResult)
        assert result.access_token == "fake_access_token"
        assert result.refresh_token == "fake_refresh_token"
        assert result.email == "test@example.com"
        assert result.user_id == str(self.test_user_id)
        assert result.role == "user"

        # Verificar que se guardó una sesión
        self.session_repo.save.assert_called_once()

        # Verificar que se generaron los tokens
        self.token_provider.generate_access_token.assert_called_once()
        self.token_provider.generate_refresh_token.assert_called_once()

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_login_fails_when_user_not_found(self):
        """
        Escenario: El email no está registrado.
        Resultado: InvalidCredentialsException (no decimos "email no existe"
        por seguridad — siempre "credenciales inválidas").
        """
        # ARRANGE
        self.user_repo.get_by_email.return_value = None  # ← no existe

        # ACT + ASSERT
        with pytest.raises(InvalidCredentialsException):
            self.use_case.execute("noexiste@example.com", "123456")

        # No se debe crear sesión ni generar tokens
        self.session_repo.save.assert_not_called()
        self.token_provider.generate_access_token.assert_not_called()

    def test_login_fails_when_password_is_wrong(self):
        """
        Escenario: El usuario existe pero la contraseña es incorrecta.
        Resultado: InvalidCredentialsException.
        """
        # ARRANGE
        self.user_repo.get_by_email.return_value = self.test_user
        self.password_hasher.verify.return_value = False  # ← contraseña incorrecta

        # ACT + ASSERT
        with pytest.raises(InvalidCredentialsException):
            self.use_case.execute("test@example.com", "wrong_password")

        # No se debe crear sesión
        self.session_repo.save.assert_not_called()
