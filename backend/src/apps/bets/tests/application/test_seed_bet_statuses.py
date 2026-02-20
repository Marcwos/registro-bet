"""
Tests — Use Case: SeedBetStatuses

Testeamos:
  - Crea los 4 estados cuando no existen
  - No crea duplicados si ya existen
  - Crea solo los que faltan
"""

from unittest.mock import Mock

from ...application.use_cases.seed_bet_statuses import SeedBetStatuses
from ...domain.repositories.bet_status_repository import BetStatusRepository


class TestSeedBetStatuses:
    def setup_method(self):
        self.repository = Mock(spec=BetStatusRepository)
        self.use_case = SeedBetStatuses(self.repository)

    def test_seed_creates_all_statuses_when_none_exist(self):
        """Crea los 4 estados cuando la tabla está vacía."""
        self.repository.exists_by_code.return_value = False

        created = self.use_case.execute()

        assert len(created) == 4
        assert self.repository.save.call_count == 4

        codes = [s.code for s in created]
        assert "pending" in codes
        assert "won" in codes
        assert "lost" in codes
        assert "void" in codes

    def test_seed_skips_existing_statuses(self):
        """No crea duplicados si todos ya existen."""
        self.repository.exists_by_code.return_value = True

        created = self.use_case.execute()

        assert len(created) == 0
        self.repository.save.assert_not_called()

    def test_seed_creates_only_missing_statuses(self):
        """Solo crea los estados que faltan."""
        self.repository.exists_by_code.side_effect = lambda code: code in ["pending", "won"]

        created = self.use_case.execute()

        assert len(created) == 2
        assert self.repository.save.call_count == 2

        codes = [s.code for s in created]
        assert "lost" in codes
        assert "void" in codes
