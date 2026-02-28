from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.user_id import UserId
from ..mappers.user_mapper import UserMapper
from ..models.user_model import UserModel


class DjangoUserRepository(UserRepository):
    def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        if UserModel.objects.filter(id=user.id.value).exists():
            model._state.adding = False
            model.save(
                update_fields=[
                    "email",
                    "password_hash",
                    "role",
                    "is_email_verified",
                    "created_at",
                    "updated_at",
                ]
            )
        else:
            model.save()

    def get_by_id(self, user_id: UserId) -> User | None:
        try:
            model = UserModel.objects.get(id=user_id.value)
            return UserMapper.to_domain(model)
        except UserModel.DoesNotExist:
            return None

    def get_by_email(self, email: Email) -> User | None:
        try:
            model = UserModel.objects.get(email=email.value)
            return UserMapper.to_domain(model)
        except UserModel.DoesNotExist:
            return None

    def exists_by_email(self, email: Email) -> bool:
        return UserModel.objects.filter(email=email.value).exists()

    def count_all(self) -> int:
        return UserModel.objects.count()
