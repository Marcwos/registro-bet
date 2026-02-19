"""
Tests unitarios para SendVerificationEmail use case.

Escenarios:
  - Happy path: genera código, guarda verificación y envía email
  - UserNotFoundException: usuario no existe
  - EmailAlreadyVerifiedException: email ya verificado
  - CooldownNotExpiredException: código enviado hace menos de 30 segundos
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.send_verification_email import SendVerificationEmail
from ...domain.entities.email_verification import EmailVerification
from ...domain.entities.user import User
from ...domain.exceptions import (
    CooldownNotExpiredException,
    EmailAlreadyVerifiedException,
    UserNotFoundException,
)
from ...domain.repositories.email_verification_repository import EmailVerficationRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.email_sender import EmailSender
from ...domain.services.verification_code_generator import VerificationCodeGenerator
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestSendVerificationEmail:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.verification_repo = Mock(spec=EmailVerficationRepository)
        self.email_sender = Mock(spec=EmailSender)
        self.code_generator = Mock(spec=VerificationCodeGenerator)

        self.use_case = SendVerificationEmail(
            user_repository=self.user_repo,
            verification_repository=self.verification_repo,
            email_sender=self.email_sender,
            code_generator=self.code_generator,
        )

        self.test_user_id = uuid4()
        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_send_verification_email_successfully(self):
        self.user_repo.get_by_id.return_value = self.test_user
        self.verification_repo.get_latest_by_user.return_value = None
        self.code_generator.generate.return_value = "123456"

        self.use_case.execute(user_id=str(self.test_user_id))

        self.verification_repo.save.assert_called_once()
        self.email_sender.send.assert_called_once()
        self.code_generator.generate.assert_called_once()

        # Verificar que el email se envió al usuario correcto
        call_args = self.email_sender.send.call_args
        assert call_args.kwargs["to"] == "test@example.com"

    def test_send_verification_email_after_cooldown_expired(self):
        """Envía código si el último fue creado hace más de 30 segundos."""
        self.user_repo.get_by_id.return_value = self.test_user
        self.code_generator.generate.return_value = "654321"

        old_verification = EmailVerification(
            id=uuid4(),
            user_id=self.test_user_id,
            code_hash="old_hash",
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC) - timedelta(seconds=60),
            used_at=None,
            attempts=0,
        )
        self.verification_repo.get_latest_by_user.return_value = old_verification

        self.use_case.execute(user_id=str(self.test_user_id))

        self.verification_repo.save.assert_called_once()
        self.email_sender.send.assert_called_once()

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_send_verification_fails_when_user_not_found(self):
        self.user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            self.use_case.execute(user_id=str(uuid4()))

        self.verification_repo.save.assert_not_called()
        self.email_sender.send.assert_not_called()

    def test_send_verification_fails_when_email_already_verified(self):
        verified_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.user_repo.get_by_id.return_value = verified_user

        with pytest.raises(EmailAlreadyVerifiedException):
            self.use_case.execute(user_id=str(self.test_user_id))

        self.verification_repo.save.assert_not_called()
        self.email_sender.send.assert_not_called()

    def test_send_verification_fails_during_cooldown(self):
        """Rechaza si el último código fue creado hace menos de 30 segundos."""
        self.user_repo.get_by_id.return_value = self.test_user

        recent_verification = EmailVerification(
            id=uuid4(),
            user_id=self.test_user_id,
            code_hash="recent_hash",
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC) - timedelta(seconds=5),
            used_at=None,
            attempts=0,
        )
        self.verification_repo.get_latest_by_user.return_value = recent_verification

        with pytest.raises(CooldownNotExpiredException):
            self.use_case.execute(user_id=str(self.test_user_id))

        self.verification_repo.save.assert_not_called()
        self.email_sender.send.assert_not_called()
