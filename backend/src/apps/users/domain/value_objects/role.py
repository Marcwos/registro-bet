from enum import Enum


class Role(Enum):
    USER = "user"
    ADMIN = "admin"

    def is_admin(self) -> bool:
        return self is Role.ADMIN
