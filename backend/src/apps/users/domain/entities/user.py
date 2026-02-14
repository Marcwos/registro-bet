from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: UserId
    email: Email
    password_hash: str
    role: Role
    is_email_verified: bool
    created_at: datetime