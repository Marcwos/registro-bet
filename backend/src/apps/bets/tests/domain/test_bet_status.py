"""
Tests de dominio — Entidad: BetStatus

Testeamos:
  - Creación con datos válidos
  - Que is_final distingue estados finales de pendientes
  - Que el code identifica correctamente cada estado
"""

from uuid import uuid4

from ...domain.entities.bet_status import BetStatus


class TestBetStatus:
    def test_create_pending_status(self):
        """El estado pendiente NO es final."""
        status = BetStatus(id=uuid4(), name="Pendiente", code="pending", is_final=False)

        assert status.name == "Pendiente"
        assert status.code == "pending"
        assert status.is_final is False

    def test_create_won_status(self):
        """El estado ganada ES final."""
        status = BetStatus(id=uuid4(), name="Ganada", code="won", is_final=True)

        assert status.code == "won"
        assert status.is_final is True

    def test_create_lost_status(self):
        """El estado perdida ES final."""
        status = BetStatus(id=uuid4(), name="Perdida", code="lost", is_final=True)

        assert status.code == "lost"
        assert status.is_final is True

    def test_create_void_status(self):
        """El estado nula ES final."""
        status = BetStatus(id=uuid4(), name="Nula", code="void", is_final=True)

        assert status.code == "void"
        assert status.is_final is True
