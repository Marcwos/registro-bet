from src.apps.bets.domain.repositories.bet_repository import BetRepository
from src.apps.users.domain.repositories.user_repository import UserRepository

from ...domain.repositories.audit_log_repository import AuditLogRepository


class GetAdminStats:
    def __init__(
        self,
        user_repository: UserRepository,
        bet_repository: BetRepository,
        audit_log_repository: AuditLogRepository,
    ):
        self.user_repository = user_repository
        self.bet_repository = bet_repository
        self.audit_log_repository = audit_log_repository

    def execute(self) -> dict:
        return {
            "total_users": self.user_repository.count_all(),
            "total_bets": self.bet_repository.count_all(),
            "total_audit_events": self.audit_log_repository.count_all(),
        }
