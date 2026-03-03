"""
Tests de dominio — Entidad: Bet

Testeamos:
  - Creación con datos válidos
  - Campos opcionales pueden ser None
  - Los Value Objects se almacenan correctamente
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from ...domain.entities.bet import Bet
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class TestBet:
    def test_create_bet_with_valid_data(self):
        """Una Bet se crea correctamente con todos los campos."""
        bet_id = uuid4()
        user_id = uuid4()
        status_id = uuid4()
        now = datetime.now(UTC)

        bet = Bet(
            id=bet_id,
            user_id=user_id,
            title="Apuesta 1",
            stake_amount=Money(amount=Decimal("10.00")),
            odds=Odds(value=Decimal("2.50")),
            profit_expected=Decimal("15.00"),
            profit_final=None,
            status_id=status_id,
            sport_id=None,
            category_id=None,
            description="",
            is_freebet=False,
            is_boosted=False,
            placed_at=now,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

        assert bet.id == bet_id
        assert bet.user_id == user_id
        assert bet.title == "Apuesta 1"
        assert bet.stake_amount.amount == Decimal("10.00")
        assert bet.odds.value == Decimal("2.50")
        assert bet.profit_expected == Decimal("15.00")
        assert bet.profit_final is None
        assert bet.status_id == status_id
        assert bet.sport_id is None
        assert bet.category_id is None
        assert bet.settled_at is None

    def test_bet_with_optional_fields(self):
        """Una Bet puede tener sport_id y category_id."""
        sport_id = uuid4()
        category_id = uuid4()
        now = datetime.now(UTC)

        bet = Bet(
            id=uuid4(),
            user_id=uuid4(),
            title="Apuesta 1",
            stake_amount=Money(amount=Decimal("5.00")),
            odds=Odds(value=Decimal("1.80")),
            profit_expected=Decimal("4.00"),
            profit_final=Decimal("4.00"),
            status_id=uuid4(),
            sport_id=sport_id,
            category_id=category_id,
            description="Fútbol - Real Madrid vs Barcelona",
            is_freebet=False,
            is_boosted=False,
            placed_at=now,
            settled_at=now,
            created_at=now,
            updated_at=now,
        )

        assert bet.sport_id == sport_id
        assert bet.category_id == category_id
        assert bet.profit_final == Decimal("4.00")
        assert bet.settled_at is not None

    def test_bet_stake_amount_uses_money_vo(self):
        """El stake_amount es un Value Object Money."""
        now = datetime.now(UTC)
        bet = Bet(
            id=uuid4(),
            user_id=uuid4(),
            title="Test",
            stake_amount=Money(amount=Decimal("25.50")),
            odds=Odds(value=Decimal("3.00")),
            profit_expected=Decimal("51.00"),
            profit_final=None,
            status_id=uuid4(),
            sport_id=None,
            category_id=None,
            description="",
            is_freebet=False,
            is_boosted=False,
            placed_at=now,
            settled_at=None,
            created_at=now,
            updated_at=now,
        )

        assert isinstance(bet.stake_amount, Money)
        assert isinstance(bet.odds, Odds)
