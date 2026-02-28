"""
Sprint I3 — Tests de integración: Catálogos (CRUD Admin)

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

import pytest
from django.core.management import call_command

from src.apps.bets.infrastructure.models.bet_category_model import BetCategoryModel
from src.apps.bets.infrastructure.models.sport_model import SportModel

# ──────────────────────────────────────────────────────────────
# 1. Deportes (Sports)
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSportIntegration:
    def test_list_sports(self, admin_client):
        """Listar deportes → 200, lista desde BD."""
        client, _ = admin_client

        # Admin crea un deporte primero
        client.post("/api/bets/sports/", {"name": "Fútbol"}, format="json")

        # Listar deportes
        response = client.get("/api/bets/sports/", format="json")

        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) >= 1
        names = [s["name"] for s in response.data]
        assert "Fútbol" in names

    def test_admin_creates_sport(self, admin_client):
        """Admin crea deporte → 201, persistido en BD."""
        client, _ = admin_client

        response = client.post(
            "/api/bets/sports/",
            {"name": "Tenis"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["name"] == "Tenis"
        assert response.data["is_active"] is True

        # Verificar persistencia en BD
        sport = SportModel.objects.get(name="Tenis")
        assert sport is not None

    def test_non_admin_rejected_creating_sport(self, authenticated_client):
        """No-admin rechazado al crear deporte → 403."""
        client, _, _ = authenticated_client

        response = client.post(
            "/api/bets/sports/",
            {"name": "MMA"},
            format="json",
        )

        assert response.status_code == 403


# ──────────────────────────────────────────────────────────────
# 2. Categorías (BetCategory)
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBetCategoryIntegration:
    def test_admin_creates_category(self, admin_client):
        """Admin crea categoría → 201."""
        client, _ = admin_client

        response = client.post(
            "/api/bets/categories/",
            {"name": "Simple", "description": "Apuesta simple"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["name"] == "Simple"
        assert response.data["description"] == "Apuesta simple"

        # Verificar persistencia en BD
        category = BetCategoryModel.objects.get(name="Simple")
        assert category is not None


# ──────────────────────────────────────────────────────────────
# 3. Estados de apuesta (BetStatus seed)
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBetStatusIntegration:
    def test_list_seeded_statuses(self, authenticated_client):
        """Listar estados → 4 estados fijos presentes desde seed."""
        # Ejecutar seed
        call_command("seed_bet_statuses")

        client, _, _ = authenticated_client
        response = client.get("/api/bets/statuses/", format="json")

        assert response.status_code == 200
        assert len(response.data) == 4

        codes = {s["code"] for s in response.data}
        assert codes == {"pending", "won", "lost", "void"}
