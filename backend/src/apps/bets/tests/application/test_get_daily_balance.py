"""
Tests — Use Case: GetDailyBalance

Testeamos:
  - Balance diario con apuestas mixtas
  - Balance diario sin apuestas (todo en cero)
  - Que llama al repositorio con la fecha correcta
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.get_daily_balance import GetDailyBalance
from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


def _make_status(code, is_final):
    return BetStatus(id=uuid4(), name=code.capitalize(), code=code, is_final=is_final)


def _make_bet(status_id, stake="10.00", profit_final=None):
    now = datetime.now(UTC)
    return Bet(
        id=uuid4(),
        user_id=uuid4(),
        title="Test",
        stake_amount=Money(amount=Decimal(stake)),
        odds=Odds(value=Decimal("2.00")),
        profit_expected=Decimal(stake),
        profit_final=Decimal(profit_final) if profit_final else None,
        status_id=status_id,
        sport_id=None,
        category_id=None,
        description="",
        placed_at=now,
        settled_at=now if profit_final else None,
        created_at=now,
        updated_at=now,
    )


class TestGetDailyBalance:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = GetDailyBalance(self.bet_repo, self.status_repo)

        self.won = _make_status("won", True)
        self.lost = _make_status("lost", True)
        self.pending = _make_status("pending", False)
        self.status_repo.get_all.return_value = [self.won, self.lost, self.pending]

    def test_daily_balance_with_mixed_bets(self):
        """Calcula balance diario correctamente con apuestas mixtas."""
        user_id = uuid4()
        target = date(2026, 2, 21)

        self.bet_repo.get_by_user_and_date.return_value = [
            _make_bet(self.won.id, stake="10.00", profit_final="15.00"),
            _make_bet(self.lost.id, stake="8.00"),
            _make_bet(self.pending.id, stake="5.00"),
        ]

        result = self.use_case.execute(user_id=user_id, tarjet_date=target)

        assert result.tarjet_date == target
        assert result.total_won == Decimal("15.00")
        assert result.total_lost == Decimal("8.00")
        assert result.net_profit == Decimal("7.00")
        assert result.bet_count == 3
        assert result.won_count == 1
        assert result.lost_count == 1
        assert result.pending_count == 1
        self.bet_repo.get_by_user_and_date.assert_called_once_with(user_id, target)

    def test_daily_balance_empty_day(self):
        """Balance vacío cuando no hay apuestas ese día."""
        self.bet_repo.get_by_user_and_date.return_value = []

        result = self.use_case.execute(user_id=uuid4(), tarjet_date=date(2026, 2, 21))

        assert result.bet_count == 0
        assert result.net_profit == Decimal("0.00")
        assert result.total_staked == Decimal("0.00")
        assert result.total_won == Decimal("0.00")
        assert result.total_lost == Decimal("0.00")

    def test_daily_balance_only_wins(self):
        """Balance de un día con solo apuestas ganadas."""
        self.bet_repo.get_by_user_and_date.return_value = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.won.id, stake="5.00", profit_final="8.00"),
        ]

        result = self.use_case.execute(user_id=uuid4(), tarjet_date=date(2026, 2, 21))

        assert result.total_won == Decimal("28.00")
        assert result.total_lost == Decimal("0.00")
        assert result.net_profit == Decimal("28.00")
        assert result.won_count == 2

    def test_daily_balance_only_losses(self):
        """Balance de un día con solo apuestas perdidas."""
        self.bet_repo.get_by_user_and_date.return_value = [
            _make_bet(self.lost.id, stake="10.00"),
            _make_bet(self.lost.id, stake="15.00"),
        ]

        result = self.use_case.execute(user_id=uuid4(), tarjet_date=date(2026, 2, 21))

        assert result.total_won == Decimal("0.00")
        assert result.total_lost == Decimal("25.00")
        assert result.net_profit == Decimal("-25.00")
        assert result.lost_count == 2
