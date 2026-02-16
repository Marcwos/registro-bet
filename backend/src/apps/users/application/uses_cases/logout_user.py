from uuid import UUID

from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.services.token_provider import TokenProvider
from ...domain.exceptions import InvalidTokenException

class LogoutUser:

    def __init__(self, session_repository: AuthSessionRepository, token_provider: TokenProvider):
        self.session_repository = session_repository
        self.token_provider = token_provider
    
    def execute(self, refresh_token: str) -> None:
        # 1. Decodificar para obtener el session_id
        payload = self.token_provider.decode_refresh_token(refresh_token)
        session_id = UUID(payload["session_id"])

        # 2. Revocar la sesion
        session = self.session_repository.get_by_id(session_id)
        if session is None:
            raise InvalidTokenException()

        self.session_repository.revoke_by_id(session_id)