from datetime import UTC, datetime
from uuid import uuid4

from src.apps.audit.domain.services.audit_service import AuditService

from ...domain.entities.user import User
from ...domain.exceptions import UserAlreadyExistsException
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class RegisterUser:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        audit_service: AuditService | None = None,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.audit_service = audit_service

    def execute(self, email: str, password: str) -> User:
        email_vo = Email(email)

        existing = self.user_repository.get_by_email(email_vo)
        if existing is not None:
            if existing.is_email_verified:
                raise UserAlreadyExistsException()

            # Email existe pero no verificado: actualizar contraseña para permitir re-registro
            existing.password_hash = self.password_hasher.hash(password)
            existing.updated_at = datetime.now(UTC)
            self.user_repository.save(existing)
            return existing

        user = User(
            id=UserId(uuid4()),
            email=email_vo,
            password_hash=self.password_hasher.hash(password),
            role=Role.USER,
            is_email_verified=False,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.user_repository.save(user)

        if self.audit_service:
            self.audit_service.log(
                user_id=user.id.value,
                action="user_registered",
                entity_type="user",
                entity_id=user.id.value,
                metadata={"email": email},
            )

        return user
