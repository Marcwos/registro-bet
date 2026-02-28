"""
Sprint I4 — Tests de integración: CRUD Apuestas

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from src.apps.bets.infrastructure.models.bet_model import BetModel


@pytest.fixture(autouse=True)
def _seed_statuses(db):
    """Ejecuta el seed de estados antes de cada test de este módulo."""
    call_command("seed_bet_statuses")


def _create_bet(client, **overrides):
    """Helper para crear una apuesta con datos por defecto."""
    payload = {
        "stake_amount": "10.00",
        "odds": "2.50",
        "profit_expected": "15.00",
        "description": "Apuesta de prueba",
    }
    payload.update(overrides)
    return client.post("/api/bets/", payload, format="json")


# ──────────────────────────────────────────────────────────────
# 1. Crear apuesta
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCreateBetIntegration:
    def test_create_bet(self, authenticated_client):
        """Crear apuesta → 201, título auto, estado pendiente."""
        client, _, user_info = authenticated_client

        response = _create_bet(client)

        assert response.status_code == 201
        assert response.data["title"].startswith("Apuesta")
        assert response.data["stake_amount"] == "10.00"
        assert response.data["odds"] == "2.50"
        assert response.data["user_id"] == user_info["id"]

        # Verificar persistencia en BD
        bet = BetModel.objects.get(id=response.data["id"])
        assert bet is not None

    def test_create_bet_without_auth(self):
        """Crear apuesta sin autenticación → 401."""
        client = APIClient()

        response = client.post(
            "/api/bets/",
            {"stake_amount": "10.00", "odds": "2.50", "profit_expected": "15.00"},
            format="json",
        )

        assert response.status_code in (401, 403)


# ──────────────────────────────────────────────────────────────
# 2. Listar apuestas
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestListBetsIntegration:
    def test_list_user_bets(self, authenticated_client):
        """Listar apuestas → solo las del usuario autenticado."""
        client, _, _ = authenticated_client

        # Crear 2 apuestas
        _create_bet(client)
        _create_bet(client, stake_amount="20.00", odds="1.80", profit_expected="16.00")

        response = client.get("/api/bets/", format="json")

        assert response.status_code == 200
        assert len(response.data) == 2


# ──────────────────────────────────────────────────────────────
# 3. Obtener apuesta por ID
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestGetBetIntegration:
    def test_get_bet_by_id(self, authenticated_client):
        """Obtener apuesta por ID → 200."""
        client, _, _ = authenticated_client

        create_response = _create_bet(client)
        bet_id = create_response.data["id"]

        response = client.get(f"/api/bets/{bet_id}/", format="json")

        assert response.status_code == 200
        assert response.data["id"] == bet_id

    def test_access_denied_to_other_user_bet(self, authenticated_client):
        """Acceso denegado a apuesta ajena → 403."""
        client, _, _ = authenticated_client

        # Crear apuesta con el primer usuario
        create_response = _create_bet(client)
        bet_id = create_response.data["id"]

        # Crear segundo usuario y autenticarse
        other_client = APIClient()
        reg = other_client.post(
            "/api/users/register/",
            {"email": "other@example.com", "password": "securepass123"},
            format="json",
        )
        from src.apps.users.infrastructure.models.user_model import UserModel

        UserModel.objects.filter(id=reg.data["id"]).update(is_email_verified=True)
        login_resp = other_client.post(
            "/api/users/login/",
            {"email": "other@example.com", "password": "securepass123"},
            format="json",
        )
        other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_resp.data['access_token']}")

        # Intentar acceder a la apuesta del primer usuario
        response = other_client.get(f"/api/bets/{bet_id}/", format="json")

        assert response.status_code == 403


# ──────────────────────────────────────────────────────────────
# 4. Editar apuesta
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestUpdateBetIntegration:
    def test_edit_pending_bet(self, authenticated_client):
        """Editar apuesta pendiente → datos actualizados en BD."""
        client, _, _ = authenticated_client

        create_response = _create_bet(client)
        bet_id = create_response.data["id"]

        response = client.patch(
            f"/api/bets/{bet_id}/",
            {"stake_amount": "25.00", "odds": "3.00"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["stake_amount"] == "25.00"
        assert response.data["odds"] == "3.00"

        # Verificar en BD
        bet = BetModel.objects.get(id=bet_id)
        assert bet.stake_amount == 25.00
        assert bet.odds == 3.00


# ──────────────────────────────────────────────────────────────
# 5. Eliminar apuesta
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDeleteBetIntegration:
    def test_delete_bet(self, authenticated_client):
        """Eliminar apuesta → 204, eliminada de BD."""
        client, _, _ = authenticated_client

        create_response = _create_bet(client)
        bet_id = create_response.data["id"]

        response = client.delete(f"/api/bets/{bet_id}/", format="json")

        assert response.status_code == 204

        # Verificar eliminación en BD
        assert BetModel.objects.filter(id=bet_id).count() == 0


# ──────────────────────────────────────────────────────────────
# 6. Cambiar estado
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestChangeStatusIntegration:
    def test_change_status_to_won(self, authenticated_client):
        """Cambiar estado → estado actualizado + profit_final."""
        client, _, _ = authenticated_client

        create_response = _create_bet(client)
        bet_id = create_response.data["id"]

        response = client.patch(
            f"/api/bets/{bet_id}/status/",
            {"status_code": "won", "profit_final": "15.00"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["profit_final"] == "15.00"
        assert response.data["settled_at"] is not None
