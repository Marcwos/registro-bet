"""
Tests de dominio — Value Objects: DailyBalance, TotalBalance, BetHistorySummay

Testeamos:
  - Creación correcta de cada dataclass
  - Que son inmutables (frozen)
"""

from datetime import date
from decimal import Decimal

import pytest

from ...domain.value_objects.balance import (
    BetHistorySummay,
    DailyBalance,
    TotalBalance,
)


class TestDailyBalance:
    def test_create_daily_balance(self):
        """DailyBalance se crea correctamente."""
        balance = DailyBalance(
            tarjet_date=date(2026, 2, 21),
            total_staked=Decimal("100.00"),
            total_won=Decimal("50.00"),
            total_lost=Decimal("30.00"),
            total_return=Decimal("80.00"),
            net_profit=Decimal("20.00"),
            bet_count=5,
            won_count=2,
            lost_count=1,
            void_count=1,
            pending_count=1,
        )

        assert balance.tarjet_date == date(2026, 2, 21)
        assert balance.total_staked == Decimal("100.00")
        assert balance.total_won == Decimal("50.00")
        assert balance.total_lost == Decimal("30.00")
        assert balance.total_return == Decimal("80.00")
        assert balance.net_profit == Decimal("20.00")
        assert balance.bet_count == 5
        assert balance.won_count == 2
        assert balance.lost_count == 1
        assert balance.void_count == 1
        assert balance.pending_count == 1

    def test_daily_balance_is_immutable(self):
        """DailyBalance es frozen — no se puede modificar."""
        balance = DailyBalance(
            tarjet_date=date(2026, 2, 21),
            total_staked=Decimal("0"),
            total_won=Decimal("0"),
            total_lost=Decimal("0"),
            total_return=Decimal("0"),
            net_profit=Decimal("0"),
            bet_count=0,
            won_count=0,
            lost_count=0,
            void_count=0,
            pending_count=0,
        )
        with pytest.raises(AttributeError):
            balance.net_profit = Decimal("999")

    def test_daily_balance_zero_values(self):
        """DailyBalance funciona con valores en cero."""
        balance = DailyBalance(
            tarjet_date=date(2026, 1, 1),
            total_staked=Decimal("0.00"),
            total_won=Decimal("0.00"),
            total_lost=Decimal("0.00"),
            total_return=Decimal("0.00"),
            net_profit=Decimal("0.00"),
            bet_count=0,
            won_count=0,
            lost_count=0,
            void_count=0,
            pending_count=0,
        )

        assert balance.bet_count == 0
        assert balance.net_profit == Decimal("0.00")


class TestTotalBalance:
    def test_create_total_balance(self):
        """TotalBalance se crea correctamente."""
        balance = TotalBalance(
            total_staked=Decimal("500.00"),
            total_won=Decimal("200.00"),
            total_lost=Decimal("150.00"),
            total_return=Decimal("350.00"),
            net_profit=Decimal("50.00"),
            bet_count=20,
            won_count=8,
            lost_count=7,
            void_count=2,
            pending_count=3,
        )

        assert balance.total_staked == Decimal("500.00")
        assert balance.total_won == Decimal("200.00")
        assert balance.total_lost == Decimal("150.00")
        assert balance.total_return == Decimal("350.00")
        assert balance.net_profit == Decimal("50.00")
        assert balance.bet_count == 20
        assert balance.won_count == 8

    def test_total_balance_is_immutable(self):
        """TotalBalance es frozen."""
        balance = TotalBalance(
            total_staked=Decimal("0"),
            total_won=Decimal("0"),
            total_lost=Decimal("0"),
            total_return=Decimal("0"),
            net_profit=Decimal("0"),
            bet_count=0,
            won_count=0,
            lost_count=0,
            void_count=0,
            pending_count=0,
        )
        with pytest.raises(AttributeError):
            balance.total_won = Decimal("100")


class TestBetHistorySummary:
    def test_create_history_summary(self):
        """BetHistorySummay se crea correctamente."""
        summary = BetHistorySummay(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 21),
            total_staked=Decimal("300.00"),
            total_won=Decimal("100.00"),
            total_lost=Decimal("80.00"),
            total_return=Decimal("180.00"),
            net_profit=Decimal("20.00"),
            bet_count=15,
            won_count=5,
            lost_count=4,
            void_count=3,
            pending_count=3,
        )

        assert summary.start_date == date(2026, 2, 1)
        assert summary.end_date == date(2026, 2, 21)
        assert summary.total_staked == Decimal("300.00")
        assert summary.net_profit == Decimal("20.00")
        assert summary.bet_count == 15

    def test_history_summary_is_immutable(self):
        """BetHistorySummay es frozen."""
        summary = BetHistorySummay(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            total_staked=Decimal("0"),
            total_won=Decimal("0"),
            total_lost=Decimal("0"),
            total_return=Decimal("0"),
            net_profit=Decimal("0"),
            bet_count=0,
            won_count=0,
            lost_count=0,
            void_count=0,
            pending_count=0,
        )
        with pytest.raises(AttributeError):
            summary.bet_count = 99
