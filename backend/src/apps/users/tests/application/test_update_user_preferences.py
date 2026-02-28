"""
Tests de aplicacion — Caso de uso: UpdateUserPreferences

Testeamos:
  - Actualizar solo theme_preference
  - Actualizar solo timezone
  - Actualizar ambos campos
  - Error si no se envia ningún campo (cubierto por serializer)
  - Error si el usuario no existe
"""

from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from ...application.uses_cases.update_user_preferences import UpdateUserPreferences
from ...domain.entities.user import User
from ...domain.exceptions import UserNotFoundException
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestUpdateUserPreferences:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)

        self.use_case = UpdateUserPreferences(
            user_repository=self.user_repo,
        )

        self.test_user_id = uuid4()
        self.test_user = User(
            id=UserId(self.test_user_id),
            email=Email("test@example.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            theme_preference="light",
            timezone="UTC",
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_update_theme_preference_only(self):
        """Solo actualiza theme_preference, timezone queda igual."""
        self.user_repo.get_by_id.return_value = self.test_user

        result = self.use_case.execute(
            user_id=self.test_user_id,
            theme_preference="dark",
        )

        assert result["theme_preference"] == "dark"
        assert result["timezone"] == "UTC"
        self.user_repo.save.assert_called_once()

    def test_update_timezone_only(self):
        """Solo actualiza timezone, theme_preference queda igual."""
        self.user_repo.get_by_id.return_value = self.test_user

        result = self.use_case.execute(
            user_id=self.test_user_id,
            timezone="America/Bogota",
        )

        assert result["theme_preference"] == "light"
        assert result["timezone"] == "America/Bogota"
        self.user_repo.save.assert_called_once()

    def test_update_both_fields(self):
        """Actualiza theme_preference y timezone a la vez."""
        self.user_repo.get_by_id.return_value = self.test_user

        result = self.use_case.execute(
            user_id=self.test_user_id,
            theme_preference="dark",
            timezone="Europe/Madrid",
        )

        assert result["theme_preference"] == "dark"
        assert result["timezone"] == "Europe/Madrid"
        self.user_repo.save.assert_called_once()

    def test_update_saves_user_with_new_updated_at(self):
        """Verifica que se actualiza updated_at al guardar."""
        original_updated_at = self.test_user.updated_at
        self.user_repo.get_by_id.return_value = self.test_user

        self.use_case.execute(
            user_id=self.test_user_id,
            theme_preference="dark",
        )

        saved_user = self.user_repo.save.call_args[0][0]
        assert saved_user.updated_at >= original_updated_at

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_update_fails_when_user_not_found(self):
        """Error si el usuario no existe."""
        self.user_repo.get_by_id.return_value = None

        with pytest.raises(UserNotFoundException):
            self.use_case.execute(
                user_id=uuid4(),
                theme_preference="dark",
            )

        self.user_repo.save.assert_not_called()
