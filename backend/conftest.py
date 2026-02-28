"""
Fixtures compartidos para tests de integración.

Estos fixtures usan la BD real de test de Django (se crea/destruye automáticamente).
Los tests que los usan deben estar marcados con @pytest.mark.django_db.
"""

import pytest
from rest_framework.test import APIClient

from src.apps.users.infrastructure.models.user_model import UserModel


@pytest.fixture
def api_client():
    """Cliente DRF para hacer requests a la API."""
    return APIClient()


@pytest.fixture
def register_user(api_client):
    """Registra un usuario vía la API real. Retorna una función reutilizable."""

    def _register(email="test@example.com", password="securepass123"):
        response = api_client.post(
            "/api/users/register/",
            {"email": email, "password": password},
            format="json",
        )
        return response

    return _register


@pytest.fixture
def verified_user(register_user):
    """Registra un usuario y lo marca como verificado directamente en BD."""
    response = register_user()
    user_id = response.data["id"]
    UserModel.objects.filter(id=user_id).update(is_email_verified=True)
    return {
        "id": user_id,
        "email": "test@example.com",
        "password": "securepass123",
    }


@pytest.fixture
def authenticated_client(api_client, verified_user):
    """
    Logea un usuario verificado y retorna (client, login_data, user_info).

    - client: APIClient con header Authorization ya configurado
    - login_data: dict con access_token, refresh_token, user_id, email, role
    - user_info: dict con id, email, password del usuario
    """
    response = api_client.post(
        "/api/users/login/",
        {"email": verified_user["email"], "password": verified_user["password"]},
        format="json",
    )
    login_data = response.data
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_data['access_token']}")
    return api_client, login_data, verified_user
