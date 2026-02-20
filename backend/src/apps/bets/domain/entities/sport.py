from dataclasses import dataclass
from uuid import UUID


@dataclass
class Sport:
    id: UUID
    name: str
    is_active: bool
