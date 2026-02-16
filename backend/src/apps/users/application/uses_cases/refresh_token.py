from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
import hashlib

from ...domain.entities.auth_session import AuthSession
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.services.token_provider import TokenProvider
from ...domain.exceptions import (InvalidTokenException, SessionRevokedException, UserNotFoundException)

@dataclass
class RefreshResult:
    access_token: str
    refresh_token: str

class RefreshToken:
    
    def __init__(
            self, 
            user_repository: UserRepository, 
            session_repository: AuthSessionRepository, 
            token_provider: TokenProvider
    ):
        self.user_repository = user_repository
        self.session_repository= session_repository
        self.token_provider = token_provider

    def execute(self, refresh_token : str) -> RefreshResult:
        # 1. Decodificar el refresh token
        payload = self.token_provider.decode_refresh_token(refresh_token)
        session_id = UUID(payload["session_id"])

        # 2. Buscar la sesion en bd
        session = self.session_repository.get_by_id(session_id)
        if session is None:
            raise InvalidTokenException()
        
        # 3. Verificar que no este revocada
        if session.revoked_at is not None:
            raise SessionRevokedException()
        
        # 4. Verificar que el hash coincida
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        if token_hash != session.refresh_token_hash:
            raise InvalidTokenException()
        
        # 5. Verificar que no haya expirado en BD
        if session.expires_at < datetime.now(timezone.utc):
            raise UserNotFoundException()
        
        # 6. Buscar el usuario (necesitamos su (role para el access token)
        from ...domain.value_objects.user_id import UserId
        user = self.user_repository.get_by_id(UserId(session.user_id))
        if user is None:
            raise UserNotFoundException()
        
        # 7. Revocar sesion vieja y crear una nueva (rotacion de refresh token)
        self.session_repository.revoke_by_id(session_id)

        new_session_id = uuid4()
        new_refresh_token = self.token_provider.generate_refresh_token(new_session_id)

        new_session = AuthSession(
            id=new_session_id,
            user_id=session.user_id,
            refresh_token_hash=hashlib.sha256(new_refresh_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            revoked_at=None,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
        )
        self.session_repository.save(new_session)

        # 8. Generar un nuevo access token
        new_access_token = self.token_provider.generate_access_token(user_id=user.id.value)

        return RefreshResult(access_token=new_access_token, refresh_token=new_access_token)