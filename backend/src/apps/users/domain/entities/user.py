from dataclasses import dataclass
from datetime import datetime

from ..value_objects.email import Email
from ..value_objects.role import Role
from ..value_objects.user_id import UserId


@dataclass
class User:
    id: UserId
    email: Email
    password_hash: str
    role: Role
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
