"""
Tests de dominio — Value Object: Role

Role es un Enum, por lo que testeamos:
  - Que los valores definidos existen
  - Que el método de negocio is_admin() funciona correctamente
  - Que valores no permitidos fallan
"""

import pytest

from ...domain.value_objects.role import Role


class TestRole:

    def test_user_role_exists(self):
        """El rol USER tiene valor 'user'."""
        assert Role.USER.value == "user"

    def test_admin_role_exists(self):
        """El rol ADMIN tiene valor 'admin'."""
        assert Role.ADMIN.value == "admin"

    def test_is_admin_returns_true_for_admin(self):
        """is_admin() devuelve True solo para ADMIN."""
        assert Role.ADMIN.is_admin() is True

    def test_is_admin_returns_false_for_user(self):
        """is_admin() devuelve False para USER."""
        assert Role.USER.is_admin() is False

    def test_invalid_role_raises_error(self):
        """Un valor que no existe en el Enum lanza ValueError."""
        with pytest.raises(ValueError):
            Role("superadmin")
