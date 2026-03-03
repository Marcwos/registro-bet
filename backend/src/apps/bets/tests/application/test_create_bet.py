"""
Tests — Use Case: CreateBet

Testeamos:
  - Crear apuesta exitosamente
  - Título automático "Apuesta N"
  - profit_expected ingresado por el usuario
  - Falla con monto inválido
  - Falla con cuota inválida
  - Falla si no existe el estado pendiente
  - Falla con profit_expected negativo
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.create_bet import CreateBet
from ...domain.entities.bet_status import BetStatus
from ...domain.exceptions import (
    BetStatusNotFoundException,
    InvalidBetTypeException,
    InvalidOddsException,
    InvalidProfitExpectedException,
    InvalidStakeAmountException,
)
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository


class TestCreateBet:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = CreateBet(self.bet_repo, self.status_repo)

        self.pending_status = BetStatus(id=uuid4(), name="Pendiente", code="pending", is_final=False)
        self.status_repo.get_by_code.return_value = self.pending_status
        self.bet_repo.count_by_user_and_date.return_value = 0

    def test_create_bet_successfully(self):
        """Crea una apuesta con datos válidos."""
        user_id = uuid4()

        bet = self.use_case.execute(
            user_id=user_id,
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.50"),
            profit_expected=Decimal("15.00"),
        )

        assert bet.user_id == user_id
        assert bet.stake_amount.amount == Decimal("10.00")
        assert bet.odds.value == Decimal("2.50")
        assert bet.profit_expected == Decimal("15.00")
        assert bet.status_id == self.pending_status.id
        assert bet.settled_at is None
        self.bet_repo.save.assert_called_once()

    def test_create_bet_auto_title_first_of_day(self):
        """El título es 'Apuesta 1' si es la primera del día."""
        self.bet_repo.count_by_user_and_date.return_value = 0

        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("5.00"),
            odds=Decimal("1.50"),
            profit_expected=Decimal("2.50"),
        )

        assert bet.title == "Apuesta 1"

    def test_create_bet_auto_title_increments(self):
        """El título incrementa según apuestas existentes del día."""
        self.bet_repo.count_by_user_and_date.return_value = 3

        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("5.00"),
            odds=Decimal("1.50"),
            profit_expected=Decimal("2.50"),
        )

        assert bet.title == "Apuesta 4"

    def test_create_bet_stores_user_profit_expected(self):
        """profit_expected es el valor ingresado por el usuario."""
        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.50"),
            profit_expected=Decimal("20.00"),
        )

        # El usuario ingresa la ganancia esperada directamente
        assert bet.profit_expected == Decimal("20.00")

    def test_create_bet_with_custom_placed_at(self):
        """Permite establecer fecha para registrar apuestas pasadas."""
        past = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)

        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.00"),
            profit_expected=Decimal("10.00"),
            placed_at=past,
        )

        assert bet.placed_at == past

    def test_create_bet_with_profit_final(self):
        """Permite establecer ganancia real al crear."""
        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.00"),
            profit_expected=Decimal("10.00"),
            profit_final=Decimal("10.00"),
        )

        assert bet.profit_final == Decimal("10.00")

    def test_create_bet_fails_with_invalid_stake(self):
        """Falla si el monto es inválido (0 o negativo)."""
        with pytest.raises(InvalidStakeAmountException):
            self.use_case.execute(
                user_id=uuid4(),
                stake_amount=Decimal("0"),
                odds=Decimal("2.00"),
                profit_expected=Decimal("10.00"),
            )

        self.bet_repo.save.assert_not_called()

    def test_create_bet_fails_with_invalid_odds(self):
        """Falla si la cuota es <= 1.00."""
        with pytest.raises(InvalidOddsException):
            self.use_case.execute(
                user_id=uuid4(),
                stake_amount=Decimal("10.00"),
                odds=Decimal("1.00"),
                profit_expected=Decimal("10.00"),
            )

        self.bet_repo.save.assert_not_called()

    def test_create_bet_fails_when_pending_status_not_found(self):
        """Falla si no se ha cargado el seed de estados."""
        self.status_repo.get_by_code.return_value = None

        with pytest.raises(BetStatusNotFoundException):
            self.use_case.execute(
                user_id=uuid4(),
                stake_amount=Decimal("10.00"),
                odds=Decimal("2.00"),
                profit_expected=Decimal("10.00"),
            )

        self.bet_repo.save.assert_not_called()

    def test_create_bet_fails_with_negative_profit_expected(self):
        """Falla si la ganancia esperada es negativa."""
        with pytest.raises(InvalidProfitExpectedException):
            self.use_case.execute(
                user_id=uuid4(),
                stake_amount=Decimal("10.00"),
                odds=Decimal("2.00"),
                profit_expected=Decimal("-5.00"),
            )

        self.bet_repo.save.assert_not_called()

    def test_create_freebet_successfully(self):
        """Crea una apuesta freebet (bono) con is_freebet=True."""
        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.00"),
            profit_expected=Decimal("10.00"),
            is_freebet=True,
        )

        assert bet.is_freebet is True
        assert bet.is_boosted is False
        self.bet_repo.save.assert_called_once()

    def test_create_boosted_bet_successfully(self):
        """Crea una apuesta con bonificaci\u00f3n (boost)."""
        bet = self.use_case.execute(
            user_id=uuid4(),
            stake_amount=Decimal("10.00"),
            odds=Decimal("2.00"),
            profit_expected=Decimal("25.00"),
            is_boosted=True,
        )

        assert bet.is_boosted is True
        assert bet.is_freebet is False
        self.bet_repo.save.assert_called_once()

    def test_create_bet_fails_with_both_freebet_and_boosted(self):
        """Falla si se marca bono y bonificaci\u00f3n al mismo tiempo."""
        with pytest.raises(InvalidBetTypeException):
            self.use_case.execute(
                user_id=uuid4(),
                stake_amount=Decimal("10.00"),
                odds=Decimal("2.00"),
                profit_expected=Decimal("10.00"),
                is_freebet=True,
                is_boosted=True,
            )

        self.bet_repo.save.assert_not_called()
