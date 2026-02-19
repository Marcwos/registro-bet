"""
Tests unitarios para ChangePassword use case.

Escenarios:
  - Happy path: cambia contraseña + revoca todas las sesiones (regla 32)
  - UserNotFoundException
  - InvalidPasswordException (contraseña actual incorrecta)
"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.change_password import ChangePassword
from ...domain.entities.user import User
from ...domain.exceptions import InvalidPasswordException, UserNotFoundException
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestChangePassword:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.password_hasher = Mock(spec=PasswordHasher)

        self.use_case = ChangePassword(
            user_repository=self.user_repo,
            session_repository=self.session_repo,
            password_hasher=self.password_hasher,
        )

        self.test_user_id = uuid4()
        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="old_hashed_password",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_change_password_successfully(self):
        self.user_repo.get_by_id.return_value = self.test_user
        self.password_hasher.verify.return_value = True
        self.password_hasher.hash.return_value = "new_hashed_password"

        self.use_case.execute(
            user_id=str(self.test_user_id),
            current_password="OldPassword123",
            new_password="NewPassword456",
        )

        # Verificar que se verificó la contraseña actual
        self.password_hasher.verify.assert_called_once_with("OldPassword123", "old_hashed_password")

        # Verificar que se hasheó la nueva contraseña
        self.password_hasher.hash.assert_called_once_with("NewPassword456")

        # Verificar que se guardó el usuario con nueva contraseña
        self.user_repo.save.assert_called_once()
        saved_user = self.user_repo.save.call_args[0][0]
        assert saved_user.password_hash == "new_hashed_password"

        # Verificar que se revocaron TODAS las sesiones (regla 32)
        self.session_repo.revoke_all_by_user.assert_called_once_with(self.test_user_id)

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_change_password_fails_when_user_not_found(self):
        self.user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            self.use_case.execute(str(uuid4()), "old", "new")

        self.user_repo.save.assert_not_called()
        self.session_repo.revoke_all_by_user.assert_not_called()

    def test_change_password_fails_when_current_password_is_wrong(self):
        self.user_repo.get_by_id.return_value = self.test_user
        self.password_hasher.verify.return_value = False

        with pytest.raises(InvalidPasswordException):
            self.use_case.execute(
                user_id=str(self.test_user_id),
                current_password="WrongPassword",
                new_password="NewPassword456",
            )

        self.user_repo.save.assert_not_called()
        self.session_repo.revoke_all_by_user.assert_not_called()
        self.password_hasher.hash.assert_not_called()
