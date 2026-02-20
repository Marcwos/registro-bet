from uuid import uuid4

from ...domain.entities.bet_status import BetStatus
from ...domain.repositories.bet_status_repository import BetStatusRepository

DEFAULT_STATUSES = [
    {"name": "Pendiente", "code": "pending", "is_final": False},
    {"name": "Ganada", "code": "won", "is_final": True},
    {"name": "Perdida", "code": "lost", "is_final": True},
    {"name": "Nula", "code": "void", "is_final": True},
]


class SeedBetStatuses:
    def __init__(self, status_repository: BetStatusRepository):
        self.status_repository = status_repository

    def execute(self) -> list[BetStatus]:
        """Crea los estados defecto si no existen. Retorna los creados."""
        created = []

        for status_data in DEFAULT_STATUSES:
            if not self.status_repository.exists_by_code(status_data["code"]):
                bet_status = BetStatus(
                    id=uuid4(),
                    name=status_data["name"],
                    code=status_data["code"],
                    is_final=status_data["is_final"],
                )
                self.status_repository.save(bet_status)
                created.append(bet_status)

        return created
