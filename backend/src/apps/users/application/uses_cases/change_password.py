from datetime import UTC, datetime

from src.apps.audit.domain.services.audit_service import AuditService

from ...domain.exceptions import InvalidPasswordException, UserNotFoundException
from ...domain.repositories.auth_session_repository import AuthSessionRepository
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.value_objects.user_id import UserId


class ChangePassword:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: AuthSessionRepository,
        password_hasher: PasswordHasher,
        audit_service: AuditService | None = None,
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.password_hasher = password_hasher
        self.audit_service = audit_service

    def execute(self, user_id: str, current_password: str, new_password: str) -> None:
        # 1. Buscar usuario
        user = self.user_repository.get_by_id(UserId(user_id))
        if user is None:
            raise UserNotFoundException()

        # 2. Verificar contraseña actual
        if not self.password_hasher.verify(current_password, user.password_hash):
            raise InvalidPasswordException()

        # 3. Cambiar contraseña
        user.password_hash = self.password_hasher.hash(new_password)
        user.updated_at = datetime.now(UTC)
        self.user_repository.save(user)

        # 4. Invalidad TODAS las sessiones activas
        self.session_repository.revoke_all_by_user(user.id.value)

        if self.audit_service:
            self.audit_service.log(
                user_id=user.id.value,
                action="password_changed",
                entity_type="user",
                entity_id=user.id.value,
            )
