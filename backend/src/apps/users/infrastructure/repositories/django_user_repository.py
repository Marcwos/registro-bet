from typing import Optional

from ...domain.repositories.user_repository import UserRepository
from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.user_id import UserId

from ..models.user_model import UserModel
from ..mappers.user_mapper import UserMapper

class DjangoUserRepository(UserRepository):
    
    def save(self, user: User) -> None:
        model = UserMapper.to_model(user)
        model.save()
    
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        try:
            model = UserModel.objects.get(id=user_id.value)
            return UserMapper.to_domain(model)
        except UserModel.DoesNotExist:
            return None
    
    def get_by_email(self, email: Email) -> Optional[User]:
        try:
            model = UserModel.objects.get(email=email.value)
            return UserMapper.to_domain(model)
        except UserModel.DoesNotExist:
            return None
        
    def exists_by_email(self, email: Email) -> bool:
        return UserModel.objects.filter(email=email.value).exists()