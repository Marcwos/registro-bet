"""
Tests de dominio — Value Object: Odds

Testeamos:
  - Creación con cuota válida
  - Falla con cuota <= 1.00
  - Falla con cuota exactamente 1.00
  - Falla con más de 2 decimales
  - Odds es inmutable (frozen)
"""

from decimal import Decimal

import pytest

from ...domain.value_objects.odds import Odds


class TestOdds:
    def test_create_odds_with_valid_value(self):
        """Un Odds se crea correctamente con cuota > 1.00."""
        odds = Odds(value=Decimal("2.50"))
        assert odds.value == Decimal("2.50")

    def test_create_odds_with_high_value(self):
        """Un Odds acepta cuotas altas."""
        odds = Odds(value=Decimal("15.00"))
        assert odds.value == Decimal("15.00")

    def test_odds_fails_with_one(self):
        """Falla si la cuota es exactamente 1.00."""
        with pytest.raises(ValueError, match="mayor a 1.00"):
            Odds(value=Decimal("1.00"))

    def test_odds_fails_with_less_than_one(self):
        """Falla si la cuota es menor a 1.00."""
        with pytest.raises(ValueError, match="mayor a 1.00"):
            Odds(value=Decimal("0.50"))

    def test_odds_fails_with_more_than_two_decimals(self):
        """Falla si tiene más de 2 decimales."""
        with pytest.raises(ValueError, match="2 decimales"):
            Odds(value=Decimal("1.234"))

    def test_odds_is_immutable(self):
        """Odds es frozen dataclass."""
        odds = Odds(value=Decimal("2.00"))
        with pytest.raises(AttributeError):
            odds.value = Decimal("3.00")
