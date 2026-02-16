from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AuthSession:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None
    user_agent: str
    ip_address: str
