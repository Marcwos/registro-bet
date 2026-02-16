"""
Tests de dominio — Entidad: User

La entidad User es un dataclass. Testeamos:
  - Que se puede crear con datos válidos
  - Que sus propiedades almacenan los valores correctos
  - Que tiene la estructura esperada
"""

from datetime import UTC, datetime
from uuid import uuid4

from ...domain.entities.user import User
from ...domain.value_objects.email import Email
from ...domain.value_objects.role import Role
from ...domain.value_objects.user_id import UserId


class TestUser:
    def setup_method(self):
        """Datos base para crear un User válido."""
        self.user_id = UserId(uuid4())
        self.email = Email("test@example.com")
        self.now = datetime.now(UTC)

    def test_create_user_with_valid_data(self):
        """Un User se crea correctamente con todos los campos requeridos."""
        user = User(
            id=self.user_id,
            email=self.email,
            password_hash="hashed_password",
            role=Role.USER,
            is_email_verified=False,
            created_at=self.now,
            updated_at=self.now,
        )

        assert user.id == self.user_id
        assert user.email == self.email
        assert user.password_hash == "hashed_password"
        assert user.role == Role.USER
        assert user.is_email_verified is False
        assert user.created_at == self.now
        assert user.updated_at == self.now

    def test_user_email_value_is_accessible(self):
        """Se puede acceder al valor del email a través del value object."""
        user = User(
            id=self.user_id,
            email=self.email,
            password_hash="hash",
            role=Role.USER,
            is_email_verified=False,
            created_at=self.now,
            updated_at=self.now,
        )
        assert user.email.value == "test@example.com"

    def test_user_with_admin_role(self):
        """Un User puede tener rol ADMIN."""
        user = User(
            id=self.user_id,
            email=self.email,
            password_hash="hash",
            role=Role.ADMIN,
            is_email_verified=True,
            created_at=self.now,
            updated_at=self.now,
        )
        assert user.role == Role.ADMIN
        assert user.role.is_admin() is True
