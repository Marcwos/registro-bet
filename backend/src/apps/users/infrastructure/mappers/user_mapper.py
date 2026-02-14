from ...domain.entities.user import User
from ...domain.value_objects.user_id import UserId
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ..models.user_model import UserModel

class UserMapper:

    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            password_hash=model.password_hash,
            role=Role(model.role),
            is_email_verified=model.is_email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=entity.email.value,
            password_hash=entity.password_hash,
            role=entity.role.value,
            is_email_verified=entity.is_email_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )