import hashlib
from datetime import UTC, datetime

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

MAX_RESET_ATTEMPT = 5


class ResetPassword:
    def __init__(
        self,
        user_repository: UserRepository,
        verification_repository: EmailVerficationRepository,
        session_repository: AuthSessionRepository,
        password_hasher: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository
        self.session_repository = session_repository
        self.password_hasher = password_hasher

    def execute(self, email: str, code: str, new_password: str) -> None:
        # 1. Buscar usuario
        email_vo = Email(email)
        user = self.user_repository.get_by_email(email_vo)
        if user is None:
            raise UserNotFoundException()

        # 2. Buscar codigo mas reciente
        verification = self.verification_repository.get_latest_by_user(user.id.value)
        if verification is None:
            raise VerificationCodeNotFoundException()

        # 3. Verificar que sea del proposito correcto
        if verification.purpose != "password_recovery":
            raise VerificationCodeNotFoundException()

        # 4. Verificar que no haya sido usado
        if verification.used_at is not None:
            raise VerificationCodeNotFoundException()

        # 5. Verificar limite de intentos
        if verification.attempts >= MAX_RESET_ATTEMPT:
            raise MaxAttemptExceededException()

        # 6. Verificar que no haya expirado
        if verification.expires_at < datetime.now(UTC):
            raise ExpiredVerificationCodeException()

        # 7. Comparar el hash del codigo recibido con el guardado
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash != verification.code_hash:
            self.verification_repository.increment_attempts(verification.id)
            raise InvalidVerificationCodeException()

        # 8. Marcar codigo como usado
        self.verification_repository.mark_as_used(verification.id)

        # 9 . Cambiar contraseña
        user.password_hash = self.password_hasher.hash(new_password)
        user.updated_at = datetime.now(UTC)
        self.user_repository.save(user)

        # 10. Invalidad TODAS las sesiones activas
        self.session_repository.revoke_all_by_user(user.id.value)
