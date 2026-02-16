from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from ...domain.entities.auth_session import AuthSession
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...infrastructure.models.auth_session_model import AuthSessionModel
from ...infrastructure.mappers.auth_session_mapper import AuthSessionMapper

class DjandoAuthSessionRepository(AuthSessionRepository):

    def save(self, session: AuthSession) -> None:
        model = AuthSessionMapper.to_model(session)
        model.save()

    def get_by_id(self, session_id: UUID) -> Optional[AuthSession]:
        try: 
            model = AuthSessionModel.objects.get(id=session_id)
            return AuthSessionMapper.to_domain(model)
        except AuthSessionModel.DoesNotExist:
            return None
        
    def revoke_by_id(self, session_id: UUID) -> None:
        AuthSessionModel.objects.filter(id=session_id).update(
            revoked_at=datetime.now(timezone.utc)
        )
    
    def revoke_all_by_user(self, user_id: UUID) -> None:
        AuthSessionModel.objects.filter(
            user_id=user_id,
            revoked_at__isnull=True,
        ).update(revoked_at=datetime.now(timezone.utc))