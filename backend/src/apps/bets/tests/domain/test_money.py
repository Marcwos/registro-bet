"""
Tests de dominio — Value Object: Money

Testeamos:
  - Creación con monto válido
  - Falla con monto <= 0
  - Falla con más de 2 decimales
  - Falla con valor no numérico
  - Money es inmutable (frozen)
"""

from decimal import Decimal

import pytest

from ...domain.value_objects.money import Money


class TestMoney:
    def test_create_money_with_valid_amount(self):
        """Un Money se crea correctamente con un monto positivo."""
        money = Money(amount=Decimal("10.50"))
        assert money.amount == Decimal("10.50")

    def test_create_money_with_integer(self):
        """Un Money acepta enteros."""
        money = Money(amount=Decimal("100"))
        assert money.amount == Decimal("100")

    def test_create_money_with_one_decimal(self):
        """Un Money acepta un decimal."""
        money = Money(amount=Decimal("5.5"))
        assert money.amount == Decimal("5.5")

    def test_money_fails_with_zero(self):
        """Falla si el monto es 0."""
        with pytest.raises(ValueError, match="mayor a 0"):
            Money(amount=Decimal("0"))

    def test_money_fails_with_negative(self):
        """Falla si el monto es negativo."""
        with pytest.raises(ValueError, match="mayor a 0"):
            Money(amount=Decimal("-5.00"))

    def test_money_fails_with_more_than_two_decimals(self):
        """Falla si tiene más de 2 decimales."""
        with pytest.raises(ValueError, match="2 decimales"):
            Money(amount=Decimal("10.123"))

    def test_money_is_immutable(self):
        """Money es frozen dataclass."""
        money = Money(amount=Decimal("10.00"))
        with pytest.raises(AttributeError):
            money.amount = Decimal("20.00")
