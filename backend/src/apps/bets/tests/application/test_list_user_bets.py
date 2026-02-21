"""
Tests — Use Case: ListUserBets

Testeamos:
  - Retorna apuestas del usuario
  - Retorna lista vacía si no tiene apuestas
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.list_user_bets import ListUserBets
from ...domain.entities.bet import Bet
from ...domain.repositories.bet_repository import BetRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


def _make_bet(user_id):
    now = datetime.now(UTC)
    return Bet(
        id=uuid4(),
        user_id=user_id,
        title="Apuesta 1 del dia",
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


class TestListUserBets:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.use_case = ListUserBets(self.bet_repo)

    def test_list_returns_user_bets(self):
        """Retorna todas las apuestas del usuario."""
        user_id = uuid4()
        bets = [_make_bet(user_id), _make_bet(user_id)]
        self.bet_repo.get_by_user.return_value = bets

        result = self.use_case.execute(user_id=user_id)

        assert len(result) == 2
        self.bet_repo.get_by_user.assert_called_once_with(user_id)

    def test_list_returns_empty(self):
        """Retorna lista vacía si no hay apuestas."""
        self.bet_repo.get_by_user.return_value = []

        result = self.use_case.execute(user_id=uuid4())

        assert result == []
