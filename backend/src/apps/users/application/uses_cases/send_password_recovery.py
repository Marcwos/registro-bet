import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from ...domain.entities.email_verification import EmailVerification
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.email_sender import EmailSender
from ...domain.services.verification_code_generator import VerificationCodeGenerator
from ...domain.value_objects.email import Email

COOLDOWN_SECONDS = 30


class SendPasswordRecovery:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerification,
        email_sender: EmailSender,
        code_generator: VerificationCodeGenerator,
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository
        self.email_sender = email_sender
        self.code_generator = code_generator

    def execute(self, email: str) -> None:
        # 1. Buscar usuario por email
        email_vo = Email(email)
        user = self.user_repository.get_by_email(email_vo)
        if user is None:
            # no se revela si el correo existe
            return

        # 2. Verificar cooldown
        latest = self.verification_repository.get_latest_by_user(user.id.value)
        if latest is not None and latest.purpose == "password_recovery" and latest.used_at is None:
            elapsed = (datetime.now(UTC) - latest.created_at).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                # No revelamos nada, simplemente retornamos
                return

        # 3. Generar Codigo
        code = self.code_generator.generate()

        # 4. Guardar verification con hash
        verification = EmailVerification(
            id=uuid4(),
            user_id=user.id.value,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            purpose="password_recovery",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )
        self.verification_repository.save(verification)

        # 4. Enviar email con plantilla HTML
        from ...infrastructure.services.email_templates import build_recovery_email

        subject, plain, html = build_recovery_email(code)
        self.email_sender.send(
            to=user.email.value,
            subject=subject,
            body=plain,
            html_body=html,
        )
