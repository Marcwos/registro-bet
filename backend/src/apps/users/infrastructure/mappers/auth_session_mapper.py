from ...domain.entities.auth_session import AuthSession
from ..models.auth_session_model import AuthSessionModel

class AuthSessionMapper:

    @staticmethod
    def to_domain(model: AuthSessionModel) -> AuthSession:
        return AuthSession(
            id=model.id,
            user_id=model.user_id,
            refresh_token_hash=model.refresh_token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
        )
    
    @staticmethod
    def to_model(entity: AuthSession) -> AuthSessionModel:
        return AuthSessionModel(
            id=entity.id,
            user_id=entity.user_id,
            refresh_token_hash=entity.refresh_token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            revoked_at=entity.revoked_at,
            user_agent=entity.user_agent,
            ip_address=entity.ip_address,
        )