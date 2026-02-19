import hashlib
from datetime import UTC, datetime

from ...domain.exceptions import (
    EmailAlreadyVerifiedException,
    ExpiredVerificationCodeException,
    InvalidVerificationCodeException,
    MaxAttemptExceededException,
    UserNotFoundException,
    VerificationCodeNotFoundException,
)
from ...domain.repositories.email_verification_repository import EmailVerficationRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_id import UserId

MAX_VERIFICATION_ATTEMPTS = 5


class VerifyEmail:
    def __init__(self, user_repository: UserRepository, verification_repository: EmailVerficationRepository):
        self.user_repository = user_repository
        self.verification_repository = verification_repository

    def execute(self, user_id: str, code: str) -> None:
        # 1. Buscar usuario
        user = self.user_repository.get_by_id(UserId(user_id))
        if user is None:
            raise UserNotFoundException()

        # 2. Verificar que no este verificado
        if user.is_email_verified:
            raise EmailAlreadyVerifiedException()

        # 3. Buscar el codigo mas reciente
        verification = self.verification_repository.get_latest_by_user(user.id.value)
        if verification is None:
            raise VerificationCodeNotFoundException()

        # 4. Verificar que sea del proposito correcto
        if verification.purpose != "email_verification":
            raise VerificationCodeNotFoundException()

        # 5. Verificar que no haya sido usado
        if verification.used_at is not None:
            raise VerificationCodeNotFoundException()

        # 6. Verificar limite de intentos
        if verification.attempts >= MAX_VERIFICATION_ATTEMPTS:
            raise MaxAttemptExceededException()

        # 7. Verificar que no haya expirado
        if verification.expires_at < datetime.now(UTC):
            raise ExpiredVerificationCodeException()

        # 8. Comparar hash del codigo recibido con el guardado
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash != verification.code_hash:
            self.verification_repository.increment_attempts(verification.id)
            raise InvalidVerificationCodeException()

        # 9. Marcar codigo como usado
        self.verification_repository.mark_as_used(verification.id)

        # 10. Marcar usuario como verificado
        user.is_email_verified = True
        user.updated_at = datetime.now(UTC)
        self.user_repository.save(user)
