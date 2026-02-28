"""
Tests — Use Case: GetTotalBalance

Testeamos:
  - Balance total con apuestas variadas
  - Balance total sin apuestas
  - Que usa get_by_user del repositorio
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.get_total_balance import GetTotalBalance
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
    stake_dec = Decimal(stake)
    odds_dec = Decimal("2.00")
    return Bet(
        id=uuid4(),
        user_id=uuid4(),
        title="Test",
        stake_amount=Money(amount=stake_dec),
        odds=Odds(value=odds_dec),
        profit_expected=(stake_dec * odds_dec).quantize(Decimal("0.01")),
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


class TestGetTotalBalance:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = GetTotalBalance(self.bet_repo, self.status_repo)

        self.won = _make_status("won", True)
        self.lost = _make_status("lost", True)
        self.void = _make_status("void", True)
        self.pending = _make_status("pending", False)
        self.status_repo.get_all.return_value = [
            self.won,
            self.lost,
            self.void,
            self.pending,
        ]

    def test_total_balance_with_mixed_bets(self):
        """Calcula balance total correctamente."""
        user_id = uuid4()

        self.bet_repo.get_by_user.return_value = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.won.id, stake="20.00", profit_final="40.00"),
            _make_bet(self.lost.id, stake="15.00"),
            _make_bet(self.void.id, stake="5.00"),
        ]

        result = self.use_case.execute(user_id=user_id)

        # return=profit_final, profit = return - stake
        # won: (20-10) + (40-20) = 30
        assert result.total_won == Decimal("30.00")
        assert result.total_return == Decimal("60.00")  # 10*2 + 20*2
        assert result.total_lost == Decimal("15.00")
        assert result.net_profit == Decimal("15.00")
        assert result.total_staked == Decimal("50.00")
        assert result.bet_count == 4
        assert result.won_count == 2
        assert result.lost_count == 1
        assert result.void_count == 1
        self.bet_repo.get_by_user.assert_called_once_with(user_id)

    def test_total_balance_empty(self):
        """Balance total vacío cuando no hay apuestas."""
        self.bet_repo.get_by_user.return_value = []

        result = self.use_case.execute(user_id=uuid4())

        assert result.bet_count == 0
        assert result.net_profit == Decimal("0.00")
        assert result.total_staked == Decimal("0.00")
        assert result.total_won == Decimal("0.00")
        assert result.total_lost == Decimal("0.00")
        assert result.total_return == Decimal("0.00")

    def test_total_balance_all_lost(self):
        """Balance total negativo cuando todas son perdidas."""
        self.bet_repo.get_by_user.return_value = [
            _make_bet(self.lost.id, stake="10.00"),
            _make_bet(self.lost.id, stake="20.00"),
            _make_bet(self.lost.id, stake="5.00"),
        ]

        result = self.use_case.execute(user_id=uuid4())

        assert result.total_lost == Decimal("35.00")
        assert result.total_won == Decimal("0.00")
        assert result.total_return == Decimal("0.00")
        assert result.net_profit == Decimal("-35.00")
        assert result.lost_count == 3

    def test_total_balance_with_pending_only(self):
        """Pendientes no afectan ganancias/pérdidas."""
        self.bet_repo.get_by_user.return_value = [
            _make_bet(self.pending.id, stake="50.00"),
        ]

        result = self.use_case.execute(user_id=uuid4())

        assert result.bet_count == 1
        assert result.pending_count == 1
        assert result.net_profit == Decimal("0.00")
        assert result.total_return == Decimal("0.00")
        assert result.total_staked == Decimal("50.00")
