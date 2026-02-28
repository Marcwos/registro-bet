"""
Sprint I6 — Tests de integración: Admin + Auditoría + Preferencias

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

import pytest
from rest_framework.test import APIClient

from src.apps.users.infrastructure.models.user_model import UserModel

# ──────────────────────────────────────────────────────────────
# 1. Stats admin
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminStatsIntegration:
    def test_admin_stats_returns_real_metrics(self, admin_client, register_user):
        """Stats admin → métricas reales desde BD."""
        client, admin_info = admin_client

        # Registrar un usuario extra para que haya más datos
        register_user(email="extra@example.com", password="securepass123")

        response = client.get("/api/admin/stats/", format="json")

        assert response.status_code == 200
        data = response.data
        assert "total_users" in data
        assert "total_bets" in data
        assert "total_audit_events" in data

        # Al menos el admin + el usuario registrado por el fixture + el extra
        assert data["total_users"] >= 2
        # Como mínimo hay eventos de auditoría por register y login del admin
        assert data["total_audit_events"] >= 1


# ──────────────────────────────────────────────────────────────
# 2. No-admin rechazado
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAdminStatsPermissionIntegration:
    def test_non_admin_rejected_from_stats(self, authenticated_client):
        """No-admin → 403 en /api/admin/stats/."""
        client, _, _ = authenticated_client

        response = client.get("/api/admin/stats/", format="json")

        assert response.status_code == 403


# ──────────────────────────────────────────────────────────────
# 3. Audit logs registrados
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestAuditLogsIntegration:
    def test_audit_logs_contain_register_and_login_events(self, admin_client):
        """Audit logs → eventos de registro y login aparecen."""
        client, admin_info = admin_client

        # Registrar otro usuario para generar un evento extra de registro
        extra_client = APIClient()
        extra_client.post(
            "/api/users/register/",
            {"email": "audited@example.com", "password": "securepass123"},
            format="json",
        )

        response = client.get("/api/admin/audit-logs/", format="json")

        assert response.status_code == 200
        data = response.data
        assert "items" in data
        assert "total" in data

        # Debe haber al menos eventos del admin (register + login) + registro del extra
        assert data["total"] >= 2

        actions = [item["action"] for item in data["items"]]
        # Verificar que existen eventos de registro y login
        assert "user_registered" in actions
        assert "user_logged_in" in actions

        # Cada item tiene la estructura esperada
        first_item = data["items"][0]
        assert "id" in first_item
        assert "user_id" in first_item
        assert "action" in first_item
        assert "entity_type" in first_item
        assert "created_at" in first_item


# ──────────────────────────────────────────────────────────────
# 4. Preferencias de usuario
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestUserPreferencesIntegration:
    def test_update_theme_and_timezone(self, authenticated_client):
        """Preferencias → theme y timezone actualizados en BD."""
        client, _, user_info = authenticated_client

        response = client.patch(
            "/api/users/preferences/",
            {"theme_preference": "dark", "timezone": "America/Mexico_City"},
            format="json",
        )

        assert response.status_code == 200
        data = response.data
        assert data["theme_preference"] == "dark"
        assert data["timezone"] == "America/Mexico_City"

        # Verificar persistencia en BD
        user = UserModel.objects.get(id=user_info["id"])
        assert user.theme_preference == "dark"
        assert user.timezone == "America/Mexico_City"

    def test_update_only_theme(self, authenticated_client):
        """Preferencias → solo theme actualizado, timezone sin cambio."""
        client, _, user_info = authenticated_client

        response = client.patch(
            "/api/users/preferences/",
            {"theme_preference": "dark"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["theme_preference"] == "dark"

    def test_update_only_timezone(self, authenticated_client):
        """Preferencias → solo timezone actualizado."""
        client, _, user_info = authenticated_client

        response = client.patch(
            "/api/users/preferences/",
            {"timezone": "Europe/Madrid"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["timezone"] == "Europe/Madrid"

        # Verificar persistencia en BD
        user = UserModel.objects.get(id=user_info["id"])
        assert user.timezone == "Europe/Madrid"
