import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.apps.audit.domain.services.audit_service import AuditService

from ...domain.entities.auth_session import AuthSession
from ...domain.exceptions import EmailNotVerifiedException, InvalidCredentialsException
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.services.token_provider import TokenProvider
from ...domain.value_objects.email import Email


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    role: str


class LoginUser:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: AuthSessionRepository,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
        audit_service: AuditService | None = None,
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.password_hasher = password_hasher
        self.token_provider = token_provider
        self.audit_service = audit_service

    def execute(self, email: str, password: str, user_agent: str = "", ip_address: str = "") -> LoginResult:
        # 1. Buscar Usuario
        email_vo = Email(email)
        user = self.user_repository.get_by_email(email_vo)

        if user is None:
            raise InvalidCredentialsException()

        # 2. Verificar contraseña
        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsException()

        # 3. Verificar que el emai este verificado
        if not user.is_email_verified:
            raise EmailNotVerifiedException()

        # 4. Crear sesion
        session_id = uuid4()
        refresh_token = self.token_provider.generate_refresh_token(session_id)

        session = AuthSession(
            id=session_id,
            user_id=user.id.value,
            refresh_token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(UTC) + timedelta(days=7),
            created_at=datetime.now(UTC),
            revoked_at=None,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session_repository.save(session)

        # 5. Generar access token
        access_token = self.token_provider.generate_access_token(
            user_id=user.id.value,
            role=user.role.value,
        )

        if self.audit_service:
            self.audit_service.log(
                user_id=user.id.value,
                action="user_logged_in",
                entity_type="user",
                entity_id=user.id.value,
                metadata={"email": email},
                ip_address=ip_address,
            )

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id.value),
            email=user.email.value,
            role=user.role.value,
        )
