"""
Tests — Use Case: ListBetStatuses
"""

from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.list_bet_statuses import ListBetStatuses
from ...domain.entities.bet_status import BetStatus
from ...domain.repositories.bet_status_repository import BetStatusRepository


class TestListBetStatuses:
    def setup_method(self):
        self.repository = Mock(spec=BetStatusRepository)
        self.use_case = ListBetStatuses(self.repository)

    def test_list_statuses_returns_all(self):
        """Retorna los 4 estados de apuesta."""
        statuses = [
            BetStatus(id=uuid4(), name="Pendiente", code="pending", is_final=False),
            BetStatus(id=uuid4(), name="Ganada", code="won", is_final=True),
            BetStatus(id=uuid4(), name="Perdida", code="lost", is_final=True),
            BetStatus(id=uuid4(), name="Nula", code="void", is_final=True),
        ]
        self.repository.get_all.return_value = statuses

        result = self.use_case.execute()

        assert len(result) == 4
        self.repository.get_all.assert_called_once()

    def test_list_statuses_returns_empty(self):
        """Retorna lista vacía si no se han cargado los seeds."""
        self.repository.get_all.return_value = []

        result = self.use_case.execute()

        assert result == []
