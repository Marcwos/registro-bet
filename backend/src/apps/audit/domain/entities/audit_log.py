from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AuditLog:
    id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID | None
    metadata: dict
    ip_address: str
    created_at: datetime
