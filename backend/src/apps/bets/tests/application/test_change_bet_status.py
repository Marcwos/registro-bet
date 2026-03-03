"""
Tests — Use Case: ChangeStatus

Testeamos:
  - Cambiar de pendiente a ganada
  - Cambiar de pendiente a perdida
  - Cambiar de ganada a pendiente (rollback)
  - Sets settled_at cuando es final
  - Limpia settled_at cuando vuelve a pendiente
  - Permite actualizar profit_final junto con el cambio
  - Falla si la apuesta no existe
  - Falla si no es del usuario
  - Falla si el código de estado no existe
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.change_bet_status import ChangeStatus
from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus
from ...domain.exceptions import BetAccessDeniedException, BetNotFoundException, BetStatusNotFoundException
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class TestChangeStatus:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = ChangeStatus(self.bet_repo, self.status_repo)

        self.user_id = uuid4()
        self.bet_id = uuid4()
        self.pending_id = uuid4()
        self.won_id = uuid4()
        self.lost_id = uuid4()
        now = datetime.now(UTC)

        self.pending_status = BetStatus(id=self.pending_id, name="Pendiente", code="pending", is_final=False)
        self.won_status = BetStatus(id=self.won_id, name="Ganada", code="won", is_final=True)
        self.lost_status = BetStatus(id=self.lost_id, name="Perdida", code="lost", is_final=True)

        self.existing_bet = Bet(
            id=self.bet_id,
            user_id=self.user_id,
            title="Apuesta 1",
            stake_amount=Money(amount=Decimal("10.00")),
            odds=Odds(value=Decimal("2.50")),
            profit_expected=Decimal("15.00"),
            profit_final=None,
            status_id=self.pending_id,
            sport_id=None,
            category_id=None,
            description="",
            is_freebet=False,
            is_boosted=False,
            placed_at=now,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

    def test_change_to_won(self):
        """Cambia estado de pendiente a ganada."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = self.won_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            status_code="won",
            profit_final=Decimal("15.00"),
        )

        assert result.status_id == self.won_id
        assert result.settled_at is not None
        assert result.profit_final == Decimal("15.00")
        self.bet_repo.save.assert_called_once()

    def test_change_to_lost(self):
        """Cambia estado de pendiente a perdida."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = self.lost_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            status_code="lost",
        )

        assert result.status_id == self.lost_id
        assert result.settled_at is not None

    def test_change_back_to_pending(self):
        """Permite volver a pendiente (rollback) — regla 7."""
        self.existing_bet.status_id = self.won_id
        self.existing_bet.settled_at = datetime.now(UTC)
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            status_code="pending",
        )

        assert result.status_id == self.pending_id
        assert result.settled_at is None

    def test_change_status_sets_settled_at(self):
        """settled_at se establece al cambiar a estado final."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = self.won_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            status_code="won",
        )

        assert result.settled_at is not None

    def test_change_status_clears_settled_at_on_pending(self):
        """settled_at se limpia al volver a pendiente."""
        self.existing_bet.settled_at = datetime.now(UTC)
        self.existing_bet.status_id = self.won_id
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            status_code="pending",
        )

        assert result.settled_at is None

    def test_change_fails_when_not_found(self):
        """Falla si la apuesta no existe."""
        self.bet_repo.get_by_id.return_value = None

        with pytest.raises(BetNotFoundException):
            self.use_case.execute(bet_id=self.bet_id, user_id=self.user_id, status_code="won")

    def test_change_fails_when_not_owned(self):
        """Falla si la apuesta no es del usuario."""
        self.bet_repo.get_by_id.return_value = self.existing_bet

        with pytest.raises(BetAccessDeniedException):
            self.use_case.execute(bet_id=self.bet_id, user_id=uuid4(), status_code="won")

    def test_change_fails_with_invalid_status_code(self):
        """Falla si el código de estado no existe."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_code.return_value = None

        with pytest.raises(BetStatusNotFoundException):
            self.use_case.execute(bet_id=self.bet_id, user_id=self.user_id, status_code="invalid")
