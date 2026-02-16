from datetime import UTC, datetime
from uuid import uuid4

from ...domain.entities.user import User
from ...domain.exceptions import UserAlreadyExistsException
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class RegisterUser:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(self, email: str, password: str) -> User:
        email_vo = Email(email)

        if self.user_repository.exists_by_email(email_vo):
            raise UserAlreadyExistsException()

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

        return user
