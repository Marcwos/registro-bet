"""
Tests de dominio — Servicio: BalanceCalculator

Testeamos:
  - Balance con apuestas ganadas (usa stake * (odds - 1))
  - Balance con apuestas perdidas (resta stake_amount)
  - Balance con apuestas nulas (impacto 0)
  - Balance con apuestas pendientes (no afecta)
  - Balance mixto (todas combinadas)
  - Balance con lista vacía
  - Apuesta con status desconocido se ignora
  - Varias ganadas acumulan correctamente
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


def _make_bet(status_id, stake="10.00", profit_final=None, is_freebet=False, is_boosted=False) -> Bet:
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
        is_freebet=is_freebet,
        is_boosted=is_boosted,
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

    def test_won_bets_add_profit_real(self):
        """Ganadas suman stake * (odds - 1) al balance."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.won.id, stake="20.00", profit_final="40.00"),
        ]

        result = self.calculator.calculate(bets)

        # return=profit_final, profit = return - stake
        # (20-10) + (40-20) = 10 + 20 = 30
        assert result["total_won"] == Decimal("30.00")
        assert result["total_return"] == Decimal("60.00")  # 10*2 + 20*2
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
        assert result["total_return"] == Decimal("0.00")
        assert result["lost_count"] == 2
        assert result["net_profit"] == Decimal("-15.00")

    def test_void_bets_no_impact(self):
        """Nulas no afectan el balance."""
        bets = [_make_bet(self.void.id, stake="10.00")]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("0.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["total_return"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["void_count"] == 1

    def test_pending_bets_no_impact_on_profit(self):
        """Pendientes no afectan ganancias ni pérdidas."""
        bets = [_make_bet(self.pending.id, stake="10.00")]

        result = self.calculator.calculate(bets)

        assert result["total_won"] == Decimal("0.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["total_return"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["pending_count"] == 1
        # Pero sí se cuenta el stake
        assert result["total_staked"] == Decimal("10.00")

    def test_mixed_balance(self):
        """Balance mixto: ganada + perdida + nula + pendiente."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.lost.id, stake="8.00"),
            _make_bet(self.void.id, stake="5.00"),
            _make_bet(self.pending.id, stake="20.00"),
        ]

        result = self.calculator.calculate(bets)

        # return=20, profit = 20 - 10 = 10.00
        assert result["total_won"] == Decimal("10.00")
        assert result["total_return"] == Decimal("20.00")  # 10*2
        assert result["total_lost"] == Decimal("8.00")
        assert result["net_profit"] == Decimal("2.00")
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
        assert result["total_return"] == Decimal("0.00")
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

    def test_won_bet_without_profit_final_still_calculates(self):
        """Ganada sin profit_final usa profit_expected como retorno."""
        bets = [_make_bet(self.won.id, stake="10.00", profit_final=None)]

        result = self.calculator.calculate(bets)

        assert result["won_count"] == 1
        # profit_expected = 10 * 2.00 = 20, profit = 20 - 10 = 10
        assert result["total_won"] == Decimal("10.00")
        assert result["total_return"] == Decimal("20.00")  # 10*2

    def test_multiple_won_bets_accumulate(self):
        """Varias ganadas acumulan correctamente."""
        bets = [
            _make_bet(self.won.id, stake="5.00", profit_final="10.00"),
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),
            _make_bet(self.won.id, stake="3.00", profit_final="6.00"),
        ]

        result = self.calculator.calculate(bets)

        # profit = (10-5) + (20-10) + (6-3) = 5 + 10 + 3 = 18
        assert result["total_won"] == Decimal("18.00")
        assert result["total_return"] == Decimal("36.00")  # (5+10+3)*2
        assert result["total_staked"] == Decimal("18.00")
        assert result["net_profit"] == Decimal("18.00")
        assert result["won_count"] == 3

    # ─── Freebet (Bono) tests ────────────────────────────

    def test_freebet_lost_does_not_subtract_stake(self):
        """Freebet perdida: no resta stake del balance (no era dinero real)."""
        bets = [
            _make_bet(self.lost.id, stake="10.00", is_freebet=True),
        ]

        result = self.calculator.calculate(bets)

        assert result["total_lost"] == Decimal("0.00")
        assert result["net_profit"] == Decimal("0.00")
        assert result["lost_count"] == 1
        # Freebet no cuenta como dinero real apostado
        assert result["total_staked"] == Decimal("0.00")

    def test_freebet_won_calculates_profit_minus_stake(self):
        """Freebet ganada: ganancia = profit_final - stake."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00", is_freebet=True),
        ]

        result = self.calculator.calculate(bets)

        # return=20, profit = 20 - 10 = 10
        assert result["total_won"] == Decimal("10.00")
        assert result["total_return"] == Decimal("20.00")
        assert result["won_count"] == 1

    def test_boosted_bet_processed_as_normal(self):
        """Apuesta con Bonificaci\u00f3n (boost) se procesa exactamente como apuesta normal."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="30.00", is_boosted=True),
        ]

        result = self.calculator.calculate(bets)

        # return=30, profit = 30 - 10 = 20
        assert result["total_won"] == Decimal("20.00")
        assert result["total_lost"] == Decimal("0.00")
        assert result["total_return"] == Decimal("30.00")

    def test_freebet_mixed_with_normal_bets(self):
        """Mezcla de freebets y apuestas normales calcula correctamente."""
        bets = [
            _make_bet(self.won.id, stake="10.00", profit_final="20.00"),  # normal ganada
            _make_bet(self.lost.id, stake="10.00", is_freebet=True),  # freebet perdida
            _make_bet(self.lost.id, stake="5.00"),  # normal perdida
            _make_bet(self.won.id, stake="10.00", profit_final="20.00", is_freebet=True),  # freebet ganada
        ]

        result = self.calculator.calculate(bets)

        # Normal ganada: won += 10 (20-10)
        # Freebet perdida: lost += 0
        # Normal perdida: lost += 5
        # Freebet ganada: won += 10 (20-10)
        assert result["total_won"] == Decimal("20.00")
        assert result["total_lost"] == Decimal("5.00")
        assert result["net_profit"] == Decimal("15.00")
        assert result["won_count"] == 2
        assert result["lost_count"] == 2
