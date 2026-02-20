from dataclasses import dataclass
from uuid import UUID


@dataclass
class BetStatus:
    id: UUID
    name: str
    code: str
    is_final: bool
