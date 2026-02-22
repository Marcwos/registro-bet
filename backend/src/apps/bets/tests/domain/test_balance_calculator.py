"""
Tests de dominio — Servicio: BalanceCalculator

Testeamos:
  - Balance con apuestas ganadas (suma profit_final)
  - Balance con apuestas perdidas (resta stake_amount)
  - Balance con apuestas nulas (impacto 0)
  - Balance con apuestas pendientes (no afecta)
  - Balance mixto (todas combinadas)
  - Balance con lista vacía
  - Apuesta con status desconocido se ignora
  - Ganada sin profit_final no suma nada
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus
from ...domain.services.balance_calculator import BalanceCalculator
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


def _make_status(code: str, is_final: bool) -> BetStatus:
    return BetStatus(id=uuid4(), name=code.capitalize(), code=code, is_final=is_final)


def _make_bet(status_id, stake="10.00", profit_final=None) -> Bet:
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


class TestBalanceCalculator:
    def setup_method(self):
        self.pending = _make_status("pending", False)
        self.won = _make_status("won", True)
        self.lost = _make_status("lost", True)
        self.void = _make_status("void", True)
        self.status_map = {
            self.pending.id: self.pending,
            self.won.id: self.won,
            self.lost.id: self.lost,
            self.void.id: self.void,
        }
        self.calculator = BalanceCalculator(self.status_map)

    def test_won_bets_add_profit_final(self):
        """Ganadas suman profit_final al balance."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="15.00"),
            _make_bet(self.won.id, stake="20.00", profit_final="30.00"),
        ]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("45.00")
        assert result["won_count"] == 2
        assert result["total_staked"] == Decimal("30.00")

    def test_lost_bets_subtract_stake(self):
        """Perdidas restan stake_amount."""
        bets = [
            _make_bet(self.lost.id, stake="10.00"),
            _make_bet(self.lost.id, stake="5.00"),
        ]

        result = self.calculator.calculate(bets)

        assert result["total_lost"] == Decimal("15.00")
        assert result["lost_count"] == 2
        assert result["net_profit"] == Decimal("-15.00")

    def test_void_bets_no_impact(self):
        """Nulas no afectan el balance."""
        bets = [_make_bet(self.void.id, stake="10.00")]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("0.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["void_count"] == 1

    def test_pending_bets_no_impact_on_profit(self):
        """Pendientes no afectan ganancias ni pérdidas."""
        bets = [_make_bet(self.pending.id, stake="10.00")]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("0.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["pending_count"] == 1
        # Pero sí se cuenta el stake
        assert result["total_staked"] == Decimal("10.00")

    def test_mixed_balance(self):
        """Balance mixto: ganada + perdida + nula + pendiente."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="15.00"),
            _make_bet(self.lost.id, stake="8.00"),
            _make_bet(self.void.id, stake="5.00"),
            _make_bet(self.pending.id, stake="20.00"),
        ]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("15.00")
        assert result["total_lost"] == Decimal("8.00")
        assert result["net_profit"] == Decimal("7.00")
        assert result["total_staked"] == Decimal("43.00")
        assert result["bet_count"] == 4
        assert result["won_count"] == 1
        assert result["lost_count"] == 1
        assert result["void_count"] == 1
        assert result["pending_count"] == 1

    def test_empty_bets_list(self):
        """Lista vacía retorna todo en cero."""
        result = self.calculator.calculate([])

        assert result["total_staked"] == Decimal("0.00")
        assert result["total_won"] == Decimal("0.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["bet_count"] == 0
        assert result["won_count"] == 0
        assert result["lost_count"] == 0
        assert result["void_count"] == 0
        assert result["pending_count"] == 0

    def test_unknown_status_is_skipped(self):
        """Apuestas con status_id desconocido se ignoran (no suman nada)."""
        unknown_id = uuid4()
        bets = [_make_bet(unknown_id, stake="10.00")]

        result = self.calculator.calculate(bets)

        assert result["bet_count"] == 1
        assert result["total_staked"] == Decimal("0.00")
        assert result["won_count"] == 0
        assert result["lost_count"] == 0
        assert result["void_count"] == 0
        assert result["pending_count"] == 0

    def test_won_bet_without_profit_final_does_not_add(self):
        """Ganada sin profit_final no suma a total_won."""
        bets = [_make_bet(self.won.id, stake="10.00", profit_final=None)]

        result = self.calculator.calculate(bets)

        assert result["won_count"] == 1
        assert result["total_won"] == Decimal("0.00")

    def test_multiple_won_bets_accumulate(self):
        """Varias ganadas acumulan correctamente."""
        bets = [
            _make_bet(self.won.id, stake="5.00", profit_final="7.50"),
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.won.id, stake="3.00", profit_final="4.50"),
        ]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("32.00")
        assert result["total_staked"] == Decimal("18.00")
        assert result["net_profit"] == Decimal("32.00")
        assert result["won_count"] == 3
