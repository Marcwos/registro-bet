"""
Tests — Use Case: UpdateBet

Testeamos:
  - Actualizar apuesta pendiente libremente
  - Falla al editar cerrada sin confirmación
  - Editar cerrada con confirm=True
  - Actualizar profit_expected directamente
  - Falla si no existe
  - Falla si no es del usuario
"""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.use_cases.update_bet import UpdateBet
from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus
from ...domain.exceptions import (
    BetAccessDeniedException,
    BetNotEditableException,
    BetNotFoundException,
    InvalidBetTypeException,
    InvalidStakeAmountException,
)
from ...domain.repositories.bet_repository import BetRepository
from ...domain.repositories.bet_status_repository import BetStatusRepository
from ...domain.value_objects.money import Money
from ...domain.value_objects.odds import Odds


class TestUpdateBet:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.status_repo = Mock(spec=BetStatusRepository)
        self.use_case = UpdateBet(self.bet_repo, self.status_repo)

        self.user_id = uuid4()
        self.bet_id = uuid4()
        self.pending_status_id = uuid4()
        self.won_status_id = uuid4()
        now = datetime.now(UTC)

        self.pending_status = BetStatus(id=self.pending_status_id, name="Pendiente", code="pending", is_final=False)
        self.won_status = BetStatus(id=self.won_status_id, name="Ganada", code="won", is_final=True)

        self.existing_bet = Bet(
            id=self.bet_id,
            user_id=self.user_id,
            title="Apuesta 1",
            stake_amount=Money(amount=Decimal("10.00")),
            odds=Odds(value=Decimal("2.50")),
            profit_expected=Decimal("15.00"),
            profit_final=None,
            status_id=self.pending_status_id,
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

    def test_update_pending_bet_freely(self):
        """Actualiza una apuesta pendiente sin restricciones."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            stake_amount=Decimal("20.00"),
        )

        assert result.stake_amount.amount == Decimal("20.00")
        self.bet_repo.save.assert_called_once()

    def test_update_closed_bet_fails_without_confirm(self):
        """No permite editar apuesta cerrada sin confirm=True."""
        self.existing_bet.status_id = self.won_status_id
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.won_status

        with pytest.raises(BetNotEditableException):
            self.use_case.execute(
                bet_id=self.bet_id,
                user_id=self.user_id,
                stake_amount=Decimal("20.00"),
            )

        self.bet_repo.save.assert_not_called()

    def test_update_closed_bet_with_confirm(self):
        """Permite editar apuesta cerrada con confirm=True."""
        self.existing_bet.status_id = self.won_status_id
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.won_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            confirm=True,
            profit_final=Decimal("25.00"),
        )

        assert result.profit_final == Decimal("25.00")
        self.bet_repo.save.assert_called_once()

    def test_update_profit_expected_directly(self):
        """Actualiza profit_expected con el valor ingresado por el usuario."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            profit_expected=Decimal("25.00"),
        )

        assert result.profit_expected == Decimal("25.00")

    def test_update_description(self):
        """Actualiza la descripción."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            description="Partido importante",
        )

        assert result.description == "Partido importante"

    def test_update_fails_with_invalid_stake(self):
        """Falla si el nuevo monto es inválido."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        with pytest.raises(InvalidStakeAmountException):
            self.use_case.execute(
                bet_id=self.bet_id,
                user_id=self.user_id,
                stake_amount=Decimal("-5.00"),
            )

    def test_update_fails_when_not_found(self):
        """Falla si la apuesta no existe."""
        self.bet_repo.get_by_id.return_value = None

        with pytest.raises(BetNotFoundException):
            self.use_case.execute(bet_id=self.bet_id, user_id=self.user_id, description="test")

    def test_update_fails_when_not_owned(self):
        """Falla si la apuesta no es del usuario."""
        self.bet_repo.get_by_id.return_value = self.existing_bet

        with pytest.raises(BetAccessDeniedException):
            self.use_case.execute(bet_id=self.bet_id, user_id=uuid4(), description="test")

    def test_update_bet_to_freebet(self):
        """Actualiza apuesta pendiente a freebet."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        result = self.use_case.execute(
            bet_id=self.bet_id,
            user_id=self.user_id,
            is_freebet=True,
        )

        assert result.is_freebet is True
        assert result.is_boosted is False
        self.bet_repo.save.assert_called_once()

    def test_update_fails_with_both_freebet_and_boosted(self):
        """Falla si se intenta marcar bono y bonificaci\u00f3n al mismo tiempo."""
        self.bet_repo.get_by_id.return_value = self.existing_bet
        self.status_repo.get_by_id.return_value = self.pending_status

        with pytest.raises(InvalidBetTypeException):
            self.use_case.execute(
                bet_id=self.bet_id,
                user_id=self.user_id,
                is_freebet=True,
                is_boosted=True,
            )
