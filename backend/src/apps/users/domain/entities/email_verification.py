from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class EmailVerification:
    id: UUID
    user_id: UUID
    code_hash: str
    purpose: str
    expires_at: datetime
    created_at: datetime
    used_at: datetime | None
    attempts: int
