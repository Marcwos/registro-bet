"""
Sprint I2 — Tests de integración: Verificación Email + Recuperar Contraseña

Estos tests golpean la API real contra una BD PostgreSQL temporal.
No usan mocks: view → use case → repository → BD → respuesta.
"""

import re

import pytest
from rest_framework.test import APIClient

from src.apps.users.infrastructure.models.auth_session_model import AuthSessionModel
from src.apps.users.infrastructure.models.email_verification_model import EmailVerificationModel
from src.apps.users.infrastructure.models.user_model import UserModel


def _extract_code(captured_output: str) -> str:
    """Extrae el código de 6 dígitos impreso por ConsoleEmailSender."""
    match = re.search(r"codigo de (?:verificacion|recuperacion) es: (\d{6})", captured_output)
    assert match, f"No se encontró código en la salida de consola:\n{captured_output}"
    return match.group(1)


# ──────────────────────────────────────────────────────────────
# 1. Enviar código de verificación
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSendVerificationIntegration:
    def test_send_verification_code(self, api_client, register_user, capsys):
        """Enviar código de verificación → 200, código guardado en BD."""
        # 1. Registrar usuario (ahora envía email automáticamente)
        reg = register_user(email="verify@example.com")
        user_id = reg.data["id"]

        # 2. Limpiar verificación creada en registro para evitar cooldown
        capsys.readouterr()  # limpiar salida del registro
        EmailVerificationModel.objects.filter(user_id=user_id).delete()

        # 3. Solicitar código de verificación
        response = api_client.post(
            "/api/users/send-verification/",
            {"user_id": user_id},
            format="json",
        )

        assert response.status_code == 200

        # 3. Verificar que el código fue impreso en consola
        captured = capsys.readouterr().out
        code = _extract_code(captured)
        assert len(code) == 6

        # 4. Verificar persistencia en BD
        verification = EmailVerificationModel.objects.filter(user_id=user_id, purpose="email_verification").first()
        assert verification is not None
        assert verification.used_at is None
        assert verification.attempts == 0


# ──────────────────────────────────────────────────────────────
# 2. Verificar email
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestVerifyEmailIntegration:
    def test_verify_email_with_correct_code(self, api_client, register_user, capsys):
        """Verificar email con código correcto → 200, is_email_verified=True en BD."""
        # 1. Registrar usuario (envía código automáticamente)
        reg = register_user(email="toverify@example.com")
        user_id = reg.data["id"]

        # 2. Extraer código enviado durante el registro
        code = _extract_code(capsys.readouterr().out)

        # 3. Verificar email con el código correcto
        response = api_client.post(
            "/api/users/verify-email/",
            {"user_id": user_id, "code": code},
            format="json",
        )

        assert response.status_code == 200

        # 4. Verificar en BD que el email está verificado
        user = UserModel.objects.get(id=user_id)
        assert user.is_email_verified is True

    def test_verify_email_with_invalid_code(self, api_client, register_user, capsys):
        """Verificar email con código incorrecto → 400."""
        # 1. Registrar usuario (envía código automáticamente)
        reg = register_user(email="badcode@example.com")
        user_id = reg.data["id"]
        capsys.readouterr()  # limpiar salida del registro

        # 3. Intentar verificar con código incorrecto
        response = api_client.post(
            "/api/users/verify-email/",
            {"user_id": user_id, "code": "000000"},
            format="json",
        )

        assert response.status_code == 400


# ──────────────────────────────────────────────────────────────
# 3. Solicitar recuperación de contraseña
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPasswordRecoveryIntegration:
    def test_request_password_recovery(self, api_client, verified_user, capsys):
        """Solicitar recuperación → 200 (no revela si el email existe)."""
        capsys.readouterr()  # limpiar salida del registro

        # 1. Solicitar recuperación para un email existente
        response = api_client.post(
            "/api/users/recover-password/",
            {"email": verified_user["email"]},
            format="json",
        )

        assert response.status_code == 200

        # 2. Verificar que el código fue enviado (impreso en consola)
        captured = capsys.readouterr().out
        code = _extract_code(captured)
        assert len(code) == 6

        # 3. Verificar que se guardó en BD con purpose correcto
        verification = EmailVerificationModel.objects.filter(
            user_id=verified_user["id"], purpose="password_recovery"
        ).first()
        assert verification is not None


# ──────────────────────────────────────────────────────────────
# 4. Reset password con código válido
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestResetPasswordIntegration:
    def test_reset_password_with_valid_code(self, api_client, verified_user, capsys):
        """Reset password → contraseña cambiada, sesiones invalidadas."""
        capsys.readouterr()  # limpiar salida del registro
        email = verified_user["email"]
        old_password = verified_user["password"]

        # 1. Crear una sesión activa (login)
        api_client.post(
            "/api/users/login/",
            {"email": email, "password": old_password},
            format="json",
        )
        capsys.readouterr()  # limpiar salida de login

        # 2. Solicitar recuperación de contraseña
        api_client.post(
            "/api/users/recover-password/",
            {"email": email},
            format="json",
        )
        code = _extract_code(capsys.readouterr().out)

        # 3. Resetear contraseña con código válido
        new_password = "nuevapass456"
        response = api_client.post(
            "/api/users/reset-password/",
            {"email": email, "code": code, "new_password": new_password},
            format="json",
        )

        assert response.status_code == 200

        # 4. Verificar que TODAS las sesiones fueron revocadas
        active_sessions = AuthSessionModel.objects.filter(user_id=verified_user["id"], revoked_at__isnull=True)
        assert active_sessions.count() == 0

        # 5. Login con la nueva contraseña funciona
        login_response = api_client.post(
            "/api/users/login/",
            {"email": email, "password": new_password},
            format="json",
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.data


# ──────────────────────────────────────────────────────────────
# 5. Cambiar contraseña (autenticado)
# ──────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestChangePasswordIntegration:
    def test_change_password_authenticated(self, authenticated_client):
        """Cambiar contraseña → todas las sesiones revocadas, nueva pass funciona."""
        client, login_data, user_info = authenticated_client
        old_password = user_info["password"]
        new_password = "changedpass789"

        # 1. Cambiar contraseña
        response = client.post(
            "/api/users/change-password/",
            {"current_password": old_password, "new_password": new_password},
            format="json",
        )

        assert response.status_code == 200

        # 2. Verificar que TODAS las sesiones fueron revocadas
        active_sessions = AuthSessionModel.objects.filter(user_id=user_info["id"], revoked_at__isnull=True)
        assert active_sessions.count() == 0

        # 3. Login con nueva contraseña funciona
        fresh_client = APIClient()
        login_response = fresh_client.post(
            "/api/users/login/",
            {"email": user_info["email"], "password": new_password},
            format="json",
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.data

        # 4. Login con contraseña vieja falla
        fail_response = fresh_client.post(
            "/api/users/login/",
            {"email": user_info["email"], "password": old_password},
            format="json",
        )
        assert fail_response.status_code == 401
