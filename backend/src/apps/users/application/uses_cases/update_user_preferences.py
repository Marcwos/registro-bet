from datetime import UTC, datetime
from uuid import UUID

from ...domain.exceptions import UserNotFoundException
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_id import UserId


class UpdateUserPreferences:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(
        self,
        user_id: UUID,
        theme_preference: str | None = None,
        timezone: str | None = None,
    ) -> dict:
        user = self.user_repository.get_by_id(UserId(user_id))
        if user is None:
            raise UserNotFoundException()

        if theme_preference is not None:
            user.theme_preference = theme_preference

        if timezone is not None:
            user.timezone = timezone

        user.updated_at = datetime.now(UTC)
        self.user_repository.save(user)

        return {
            "theme_preference": user.theme_preference,
            "timezone": user.timezone,
        }
