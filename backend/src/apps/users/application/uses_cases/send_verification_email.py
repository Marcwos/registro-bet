import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from ...domain.entities.email_verification import EmailVerification
from ...domain.exceptions import CooldownNotExpiredException, EmailAlreadyVerifiedException, UserNotFoundException
from ...domain.repositories.email_verification_repository import EmailVerficationRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.email_sender import EmailSender
from ...domain.services.verification_code_generator import VerificationCodeGenerator
from ...domain.value_objects.user_id import UserId

COOLDOWN_SECONDS = 30


class SendVerificationEmail:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerficationRepository,
        email_sender: EmailSender,
        code_generator: VerificationCodeGenerator,
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository
        self.email_sender = email_sender
        self.code_generator = code_generator

    def execute(self, user_id: str) -> None:
        # 1. Buscar usuario
        user = self.user_repository.get_by_id(UserId(user_id))
        if user is None:
            raise UserNotFoundException()

        # 2. Verificar que no este ya verificado
        if user.is_email_verified:
            raise EmailAlreadyVerifiedException()

        # 3. Verificar cooldown
        latest = self.verification_repository.get_latest_by_user(user.id.value)
        if latest is not None and latest.purpose == "email_verification" and latest.used_at is None:
            elapsed = (datetime.now(UTC) - latest.created_at).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                raise CooldownNotExpiredException(int(COOLDOWN_SECONDS - elapsed))

        # 4. Generar codigo (plano todavia)
        code = self.code_generator.generate()

        # 5. Guardar verificacion con el hash del codigo (expira en 10min)
        verification = EmailVerification(
            id=uuid4(),
            user_id=user.id.value,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            created_at=datetime.now(UTC),
            used_at=None,
            attempts=0,
        )
        self.verification_repository.save(verification)

        # 6. Enviar email (el codigo en texto plano solo viaja al correo)
        self.email_sender.send(
            to=user.email.value,
            subject="Verifica tu - Registro Bet",
            body=f"Tu codigo de verificacion es: {code}\n\nExpira en 10 minutos.",
        )
