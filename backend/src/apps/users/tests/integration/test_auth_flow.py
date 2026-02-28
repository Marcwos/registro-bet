"""
Sprint I1 — Tests de integración: Auth (Registro + Login + JWT)

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

import pytest
from rest_framework.test import APIClient

from src.apps.users.infrastructure.models.auth_session_model import AuthSessionModel
from src.apps.users.infrastructure.models.user_model import UserModel

# ──────────────────────────────────────────────────────────────
# 1. Registro
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRegisterIntegration:
    def test_register_success(self, api_client):
        """Registro exitoso → 201, usuario persistido en BD real."""
        response = api_client.post(
            "/api/users/register/",
            {"email": "nuevo@example.com", "password": "securepass123"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["email"] == "nuevo@example.com"
        assert response.data["role"] == "user"
        assert response.data["is_email_verified"] is False

        # Verificar persistencia en BD
        user = UserModel.objects.get(email="nuevo@example.com")
        assert user is not None
        assert str(user.id) == response.data["id"]

    def test_register_duplicate_email(self, api_client):
        """Registro con email duplicado → 409."""
        # Primer registro
        api_client.post(
            "/api/users/register/",
            {"email": "duplicado@example.com", "password": "securepass123"},
            format="json",
        )

        # Segundo registro con mismo email
        response = api_client.post(
            "/api/users/register/",
            {"email": "duplicado@example.com", "password": "otherpass123"},
            format="json",
        )

        assert response.status_code == 409


# ──────────────────────────────────────────────────────────────
# 2. Login
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLoginIntegration:
    def test_login_unverified_email_returns_403(self, api_client, register_user):
        """Login sin verificar email → 403."""
        register_user(email="unverified@example.com")

        response = api_client.post(
            "/api/users/login/",
            {"email": "unverified@example.com", "password": "securepass123"},
            format="json",
        )

        assert response.status_code == 403

    def test_login_invalid_credentials_returns_401(self, api_client, verified_user):
        """Login con contraseña incorrecta → 401."""
        response = api_client.post(
            "/api/users/login/",
            {"email": verified_user["email"], "password": "wrongpassword"},
            format="json",
        )

        assert response.status_code == 401

    def test_login_nonexistent_email_returns_401(self, api_client):
        """Login con email que no existe → 401."""
        response = api_client.post(
            "/api/users/login/",
            {"email": "noexiste@example.com", "password": "securepass123"},
            format="json",
        )

        assert response.status_code == 401

    def test_full_register_verify_login_flow(self, api_client):
        """Flujo completo: registro → verificar email → login → recibe tokens JWT."""
        # 1. Registrar
        reg_response = api_client.post(
            "/api/users/register/",
            {"email": "flow@example.com", "password": "securepass123"},
            format="json",
        )
        assert reg_response.status_code == 201
        user_id = reg_response.data["id"]

        # 2. Simular verificación de email (directamente en BD)
        UserModel.objects.filter(id=user_id).update(is_email_verified=True)

        # 3. Login
        login_response = api_client.post(
            "/api/users/login/",
            {"email": "flow@example.com", "password": "securepass123"},
            format="json",
        )

        assert login_response.status_code == 200
        assert "access_token" in login_response.data
        assert "refresh_token" in login_response.data
        assert login_response.data["email"] == "flow@example.com"
        assert login_response.data["role"] == "user"

        # 4. Verificar que se creó una sesión en BD
        sessions = AuthSessionModel.objects.filter(user_id=user_id, revoked_at__isnull=True)
        assert sessions.count() == 1


# ──────────────────────────────────────────────────────────────
# 3. Refresh Token
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestRefreshTokenIntegration:
    def test_refresh_token_returns_new_tokens(self, authenticated_client):
        """Refresh token → nuevo par de tokens válido."""
        _, login_data, _ = authenticated_client

        fresh_client = APIClient()
        response = fresh_client.post(
            "/api/users/refresh/",
            {"refresh_token": login_data["refresh_token"]},
            format="json",
        )

        assert response.status_code == 200
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        # El refresh token siempre cambia (nueva sesión)
        assert response.data["refresh_token"] != login_data["refresh_token"]

    def test_refresh_with_invalid_token_returns_401(self):
        """Refresh con token inválido → 401."""
        client = APIClient()
        response = client.post(
            "/api/users/refresh/",
            {"refresh_token": "token.invalido.aqui"},
            format="json",
        )

        assert response.status_code == 401


# ──────────────────────────────────────────────────────────────
# 4. Logout
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLogoutIntegration:
    def test_logout_revokes_session(self, authenticated_client):
        """Logout → sesión revocada en BD, refresh posterior falla."""
        client, login_data, user_info = authenticated_client

        # 1. Logout
        response = client.post(
            "/api/users/logout/",
            {"refresh_token": login_data["refresh_token"]},
            format="json",
        )
        assert response.status_code == 200

        # 2. Verificar que la sesión está revocada en BD
        active_sessions = AuthSessionModel.objects.filter(
            user_id=user_info["id"],
            revoked_at__isnull=True,
        )
        assert active_sessions.count() == 0

        # 3. Intentar refresh con el token revocado → debe fallar
        fresh_client = APIClient()
        refresh_response = fresh_client.post(
            "/api/users/refresh/",
            {"refresh_token": login_data["refresh_token"]},
            format="json",
        )
        assert refresh_response.status_code == 401
