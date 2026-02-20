from dataclasses import dataclass
from uuid import UUID


@dataclass
class BetCategory:
    id: UUID
    name: str
    description: str
