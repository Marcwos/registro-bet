from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import hashlib

from ...domain.entities.auth_session import AuthSession
from ...domain.value_objects.email import Email
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.services.token_provider import TokenProvider
from ...domain.exceptions import InvalidCredentialsException


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    role: str

class LoginUser:

    def __init__(
            self, user_repository: UserRepository,
            session_repository: AuthSessionRepository,
            password_hasher: PasswordHasher,
            token_provider: TokenProvider
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.password_hasher = password_hasher
        self.token_provider = token_provider

    def execute(self, email:str, password: str, user_agent: str = "", ip_address: str = "") -> LoginResult:
        # 1. Buscar Usuario
        email_vo = Email(email)
        user = self.user_repository.get_by_email(email_vo)

        if user is None:
            raise InvalidCredentialsException()

        # 2. Verificar contraseña
        if not self.password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsException()

        # 3. Crear sesion
        session_id = uuid4()
        refresh_token = self.token_provider.generate_refresh_token(session_id)

        session = AuthSession(
            id=session_id,
            user_id=user.id.value,
            refresh_token_hash=hashlib.sha256(refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session_repository.save(session)

        # 4. Generar access token
        access_token = self.token_provider.generate_access_token(
            user_id=user.id.value,
            role=user.role.value,
        )

        return LoginResult(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=str(user.id.value),
            email=user.email.value,
            role=user.role.value,
        )