"""
Tests unitarios para ResetPassword use case.

Escenarios:
  - Happy path: cambia contraseña + marca código como usado + revoca sesiones
  - UserNotFoundException
  - VerificationCodeNotFoundException (sin código, propósito incorrecto, código ya usado)
  - MaxAttemptExceededException
  - ExpiredVerificationCodeException
  - InvalidVerificationCodeException (incrementa attempts)
"""

import hashlib
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.reset_password import ResetPassword
from ...domain.entities.email_verification import EmailVerification
from ...domain.entities.user import User
from ...domain.exceptions import (
    ExpiredVerificationCodeException,
    InvalidVerificationCodeException,
    MaxAttemptExceededException,
    UserNotFoundException,
    VerificationCodeNotFoundException,
)
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.email_verification_repository import EmailVerficationRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestResetPassword:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.verification_repo = Mock(spec=EmailVerficationRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.password_hasher = Mock(spec=PasswordHasher)

        self.use_case = ResetPassword(
            user_repository=self.user_repo,
            verification_repository=self.verification_repo,
            session_repository=self.session_repo,
            password_hasher=self.password_hasher,
        )

        self.test_user_id = uuid4()
        self.test_code = "123456"
        self.test_code_hash = hashlib.sha256(self.test_code.encode()).hexdigest()
        self.test_verification_id = uuid4()

        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="old_hashed_password",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.test_verification = EmailVerification(
            id=self.test_verification_id,
            user_id=self.test_user_id,
            code_hash=self.test_code_hash,
            purpose="password_recovery",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_reset_password_successfully(self):
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = self.test_verification
        self.password_hasher.hash.return_value = "new_hashed_password"

        self.use_case.execute(
            email="test@example.com",
            code=self.test_code,
            new_password="NuevaPassword123",
        )

        # Verificar que el código se marcó como usado
        self.verification_repo.mark_as_used.assert_called_once_with(self.test_verification_id)

        # Verificar que se guardó el usuario con nueva contraseña
        self.user_repo.save.assert_called_once()
        saved_user = self.user_repo.save.call_args[0][0]
        assert saved_user.password_hash == "new_hashed_password"

        # Verificar que se revocaron todas las sesiones (regla 32)
        self.session_repo.revoke_all_by_user.assert_called_once_with(self.test_user_id)

        self.password_hasher.hash.assert_called_once_with("NuevaPassword123")

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_reset_fails_when_user_not_found(self):
        self.user_repo.get_by_email.return_value = None

        with pytest.raises(UserNotFoundException):
            self.use_case.execute("noexiste@example.com", self.test_code, "nueva123")

        self.verification_repo.mark_as_used.assert_not_called()
        self.user_repo.save.assert_not_called()
        self.session_repo.revoke_all_by_user.assert_not_called()

    def test_reset_fails_when_no_verification_code_exists(self):
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = None

        with pytest.raises(VerificationCodeNotFoundException):
            self.use_case.execute("test@example.com", self.test_code, "nueva123")

        self.user_repo.save.assert_not_called()

    def test_reset_fails_when_purpose_is_wrong(self):
        wrong_purpose = EmailVerification(
            id=self.test_verification_id,
            user_id=self.test_user_id,
            code_hash=self.test_code_hash,
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = wrong_purpose

        with pytest.raises(VerificationCodeNotFoundException):
            self.use_case.execute("test@example.com", self.test_code, "nueva123")

        self.user_repo.save.assert_not_called()

    def test_reset_fails_when_code_already_used(self):
        used_verification = EmailVerification(
            id=self.test_verification_id,
            user_id=self.test_user_id,
            code_hash=self.test_code_hash,
            purpose="password_recovery",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=datetime.now(UTC),
            attempts=1,
        )
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = used_verification

        with pytest.raises(VerificationCodeNotFoundException):
            self.use_case.execute("test@example.com", self.test_code, "nueva123")

        self.user_repo.save.assert_not_called()

    def test_reset_fails_when_max_attempts_exceeded(self):
        exhausted_verification = EmailVerification(
            id=self.test_verification_id,
            user_id=self.test_user_id,
            code_hash=self.test_code_hash,
            purpose="password_recovery",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=5,
        )
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = exhausted_verification

        with pytest.raises(MaxAttemptExceededException):
            self.use_case.execute("test@example.com", self.test_code, "nueva123")

        self.user_repo.save.assert_not_called()
        self.session_repo.revoke_all_by_user.assert_not_called()

    def test_reset_fails_when_code_expired(self):
        expired_verification = EmailVerification(
            id=self.test_verification_id,
            user_id=self.test_user_id,
            code_hash=self.test_code_hash,
            purpose="password_recovery",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
            created_at=datetime.now(UTC) - timedelta(minutes=11),
            used_at=None,
            attempts=0,
        )
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = expired_verification

        with pytest.raises(ExpiredVerificationCodeException):
            self.use_case.execute("test@example.com", self.test_code, "nueva123")

        self.user_repo.save.assert_not_called()

    def test_reset_fails_with_wrong_code_and_increments_attempts(self):
        self.user_repo.get_by_email.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = self.test_verification

        with pytest.raises(InvalidVerificationCodeException):
            self.use_case.execute("test@example.com", "999999", "nueva123")

        self.verification_repo.increment_attempts.assert_called_once_with(self.test_verification_id)
        self.user_repo.save.assert_not_called()
        self.session_repo.revoke_all_by_user.assert_not_called()
