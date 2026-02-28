"""
Sprint I5 — Tests de integración: Estadísticas + Historial

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

from datetime import date

import pytest
from django.core.management import call_command


@pytest.fixture(autouse=True)
def _seed_statuses(db):
    """Ejecuta el seed de estados antes de cada test de este módulo."""
    call_command("seed_bet_statuses")


def _create_bet(client, **overrides):
    """Helper para crear una apuesta con datos por defecto."""
    payload = {
        "stake_amount": "10.00",
        "odds": "2.50",
        "profit_expected": "25.00",
    }
    payload.update(overrides)
    return client.post("/api/bets/", payload, format="json")


def _change_status(client, bet_id, status_code, profit_final=None):
    """Helper para cambiar el estado de una apuesta."""
    payload = {"status_code": status_code}
    if profit_final is not None:
        payload["profit_final"] = profit_final
    return client.patch(f"/api/bets/{bet_id}/status/", payload, format="json")


# ──────────────────────────────────────────────────────────────
# 1. Balance diario
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDailyBalanceIntegration:
    def test_daily_balance(self, authenticated_client):
        """Balance diario → cálculo real desde BD."""
        client, _, _ = authenticated_client
        today = date.today().isoformat()

        # Crear 2 apuestas y resolver una como ganada
        r1 = _create_bet(client, stake_amount="10.00", odds="2.00", profit_expected="20.00")
        r2 = _create_bet(client, stake_amount="20.00", odds="3.00", profit_expected="60.00")
        _change_status(client, r1.data["id"], "won", profit_final="20.00")
        _change_status(client, r2.data["id"], "lost")

        response = client.get(f"/api/bets/balance/daily/?date={today}", format="json")

        assert response.status_code == 200
        data = response.data
        assert data["bet_count"] == 2
        assert data["won_count"] == 1
        assert data["lost_count"] == 1
        assert float(data["total_staked"]) == 30.00
        assert float(data["total_won"]) > 0
        assert float(data["total_return"]) == 20.00  # 10*2.00
        assert float(data["total_lost"]) == 20.00


# ──────────────────────────────────────────────────────────────
# 2. Balance total
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestTotalBalanceIntegration:
    def test_total_balance(self, authenticated_client):
        """Balance total → acumulado histórico correcto."""
        client, _, _ = authenticated_client

        # Crear apuestas y resolver
        r1 = _create_bet(client, stake_amount="50.00", odds="2.00", profit_expected="100.00")
        r2 = _create_bet(client, stake_amount="30.00", odds="1.50", profit_expected="45.00")
        _change_status(client, r1.data["id"], "won", profit_final="100.00")
        _change_status(client, r2.data["id"], "lost")

        response = client.get("/api/bets/balance/total/", format="json")

        assert response.status_code == 200
        data = response.data
        assert data["bet_count"] == 2
        assert data["won_count"] == 1
        assert data["lost_count"] == 1
        assert float(data["total_staked"]) == 80.00
        assert float(data["total_return"]) == 100.00  # 50*2.00
        assert float(data["total_lost"]) == 30.00


# ──────────────────────────────────────────────────────────────
# 3. Historial con filtro por rango
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBetHistoryIntegration:
    def test_history_with_date_range(self, authenticated_client):
        """Historial con filtro por rango → summary correcto."""
        client, _, _ = authenticated_client
        today = date.today().isoformat()

        # Crear apuestas
        _create_bet(client, stake_amount="10.00", odds="2.00", profit_expected="20.00")
        _create_bet(client, stake_amount="20.00", odds="1.80", profit_expected="36.00")

        response = client.get(
            f"/api/bets/history/?start_date={today}&end_date={today}",
            format="json",
        )

        assert response.status_code == 200
        assert "summary" in response.data
        assert "bets" in response.data
        assert response.data["summary"]["bet_count"] == 2
        assert len(response.data["bets"]) == 2

    def test_history_empty_range(self, authenticated_client):
        """Historial rango vacío → respuesta vacía sin error."""
        client, _, _ = authenticated_client

        response = client.get(
            "/api/bets/history/?start_date=2020-01-01&end_date=2020-01-02",
            format="json",
        )

        assert response.status_code == 200
        assert response.data["summary"]["bet_count"] == 0
        assert len(response.data["bets"]) == 0
