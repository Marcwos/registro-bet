"""
Tests — Use Case: GetBetHistory

Testeamos:
  - Historial con apuestas en el rango
  - Historial vacío
  - Que retorna tanto apuestas como resumen (tupla)
  - Que llama al repositorio con el rango correcto
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from ...application.use_cases.get_bet_history import GetBetHistory
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


class TestGetBetHistory:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = GetBetHistory(self.bet_repo, self.status_repo)

        self.won = _make_status("won", True)
        self.lost = _make_status("lost", True)
        self.pending = _make_status("pending", False)
        self.status_repo.get_all.return_value = [self.won, self.lost, self.pending]

    def test_history_with_bets_in_range(self):
        """Retorna apuestas y resumen para el rango."""
        user_id = uuid4()
        start = date(2026, 2, 1)
        end = date(2026, 2, 21)

        mock_bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.lost.id, stake="5.00"),
        ]
        self.bet_repo.get_by_user_date_range.return_value = mock_bets

        bets, summary = self.use_case.execute(user_id=user_id, start_date=start, end_date=end)

        assert len(bets) == 2
        assert summary.start_date == start
        assert summary.end_date == end
        # return=profit_final=20, profit = 20 - 10 = 10
        assert summary.total_won == Decimal("10.00")
        assert summary.total_lost == Decimal("5.00")
        assert summary.net_profit == Decimal("5.00")
        assert summary.bet_count == 2
        assert summary.won_count == 1
        assert summary.lost_count == 1
        self.bet_repo.get_by_user_date_range.assert_called_once_with(user_id, start, end)

    def test_history_empty_range(self):
        """Rango sin apuestas retorna lista vacía y ceros."""
        self.bet_repo.get_by_user_date_range.return_value = []

        bets, summary = self.use_case.execute(
            user_id=uuid4(),
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
        )

        assert bets == []
        assert summary.bet_count == 0
        assert summary.net_profit == Decimal("0.00")
        assert summary.total_staked == Decimal("0.00")

    def test_history_returns_tuple(self):
        """El resultado es una tupla (bets, summary)."""
        self.bet_repo.get_by_user_date_range.return_value = []

        result = self.use_case.execute(
            user_id=uuid4(),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_history_bets_are_returned_as_is(self):
        """Las apuestas se retornan tal cual del repositorio."""
        bet1 = _make_bet(self.won.id, stake="10.00", profit_final="20.00")
        bet2 = _make_bet(self.pending.id, stake="5.00")
        self.bet_repo.get_by_user_date_range.return_value = [bet1, bet2]

        bets, summary = self.use_case.execute(
            user_id=uuid4(),
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
        )

        assert bets[0] is bet1
        assert bets[1] is bet2
        assert summary.pending_count == 1
        assert summary.won_count == 1

    def test_history_summary_dates_match_request(self):
        """Las fechas del summary coinciden con las solicitadas."""
        self.bet_repo.get_by_user_date_range.return_value = []
        start = date(2026, 6, 1)
        end = date(2026, 6, 30)

        _, summary = self.use_case.execute(user_id=uuid4(), start_date=start, end_date=end)

        assert summary.start_date == start
        assert summary.end_date == end
