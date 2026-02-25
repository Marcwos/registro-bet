"""
Tests — Use Case: GetBet

Testeamos:
  - Obtener apuesta exitosamente
  - Falla si no existe
  - Falla si no es del usuario
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.get_bet import GetBet
from ...domain.entities.bet import Bet
from ...domain.exceptions import BetAccessDeniedException, BetNotFoundException
from ...domain.repositories.bet_repository import BetRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class TestGetBet:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.use_case = GetBet(self.bet_repo)
        self.user_id = uuid4()
        self.bet_id = uuid4()
        now = datetime.now(UTC)

        self.existing_bet = Bet(
            id=self.bet_id,
            user_id=self.user_id,
            title="Apuesta 1",
            stake_amount=Money(amount=Decimal("10.00")),
            odds=Odds(value=Decimal("2.00")),
            profit_expected=Decimal("10.00"),
            profit_final=None,
            status_id=uuid4(),
            sport_id=None,
            category_id=None,
            description="",
            placed_at=now,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

    def test_get_bet_successfully(self):
        """Obtiene una apuesta del usuario."""
        self.bet_repo.get_by_id.return_value = self.existing_bet

        result = self.use_case.execute(bet_id=self.bet_id, user_id=self.user_id)

        assert result.id == self.bet_id
        assert result.user_id == self.user_id

    def test_get_fails_when_not_found(self):
        """Falla si la apuesta no existe."""
        self.bet_repo.get_by_id.return_value = None

        with pytest.raises(BetNotFoundException):
            self.use_case.execute(bet_id=self.bet_id, user_id=self.user_id)

    def test_get_fails_when_not_owned(self):
        """Falla si la apuesta no es del usuario."""
        self.bet_repo.get_by_id.return_value = self.existing_bet

        with pytest.raises(BetAccessDeniedException):
            self.use_case.execute(bet_id=self.bet_id, user_id=uuid4())
