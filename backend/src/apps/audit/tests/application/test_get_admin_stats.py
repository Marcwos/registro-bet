from unittest.mock import Mock

from src.apps.bets.domain.repositories.bet_repository import BetRepository
from src.apps.users.domain.repositories.user_repository import UserRepository

from ...application.use_cases.get_admin_stats import GetAdminStats
from ...domain.repositories.audit_log_repository import AuditLogRepository


class TestGetAdminStats:
    def setup_method(self):
        self.user_repository = Mock(spec=UserRepository)
        self.bet_repository = Mock(spec=BetRepository)
        self.audit_log_repository = Mock(spec=AuditLogRepository)
        self.use_case = GetAdminStats(
            user_repository=self.user_repository,
            bet_repository=self.bet_repository,
            audit_log_repository=self.audit_log_repository,
        )

    def test_get_admin_stats_returns_all_counts(self):
        self.user_repository.count_all.return_value = 10
        self.bet_repository.count_all.return_value = 50
        self.audit_log_repository.count_all.return_value = 120

        result = self.use_case.execute()

        assert result["total_users"] == 10
        assert result["total_bets"] == 50
        assert result["total_audit_events"] == 120
        self.user_repository.count_all.assert_called_once()
        self.bet_repository.count_all.assert_called_once()
        self.audit_log_repository.count_all.assert_called_once()

    def test_get_admin_stats_with_zero_data(self):
        self.user_repository.count_all.return_value = 0
        self.bet_repository.count_all.return_value = 0
        self.audit_log_repository.count_all.return_value = 0

        result = self.use_case.execute()

        assert result["total_users"] == 0
        assert result["total_bets"] == 0
        assert result["total_audit_events"] == 0
