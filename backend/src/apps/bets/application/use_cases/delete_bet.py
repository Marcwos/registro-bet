from uuid import UUID

from src.apps.audit.domain.services.audit_service import AuditService

from ...domain.exceptions import BetAccessDeniedException, BetNotFoundException
from ...domain.repositories.bet_repository import BetRepository


class DeleteBet:
    def __init__(self, bet_repository: BetRepository, audit_service: AuditService | None = None):
        self.bet_repository = bet_repository
        self.audit_service = audit_service

    def execute(self, bet_id: UUID, user_id: UUID) -> None:
        bet = self.bet_repository.get_by_id(bet_id)
        if bet is None:
            raise BetNotFoundException()

        if bet.user_id != user_id:
            raise BetAccessDeniedException

        self.bet_repository.delete(bet_id)

        if self.audit_service:
            self.audit_service.log(
                user_id=user_id,
                action="bet_deleted",
                entity_type="bet",
                entity_id=bet_id,
                metadata={"bet_title": bet.title, "stake_amount": str(bet.stake_amount.amount)},
            )
