"""
Tests de dominio — Value Object: UserId

UserId envuelve un UUID. Testeamos:
  - Creación con UUID válido
  - Inmutabilidad (frozen=True)
  - Comparación entre instancias
"""

from uuid import uuid4

import pytest

from ...domain.value_objects.user_id import UserId


class TestUserId:
    def test_create_with_valid_uuid(self):
        """Se puede crear un UserId con un UUID válido."""
        uid = uuid4()
        user_id = UserId(uid)
        assert user_id.value == uid

    def test_user_id_is_immutable(self):
        """UserId no se puede modificar después de crearlo."""
        user_id = UserId(uuid4())
        with pytest.raises(AttributeError):
            user_id.value = uuid4()

    def test_equal_user_ids(self):
        """Dos UserId con el mismo UUID son iguales (dataclass equality)."""
        uid = uuid4()
        id1 = UserId(uid)
        id2 = UserId(uid)
        assert id1 == id2

    def test_different_user_ids(self):
        """Dos UserId con UUIDs diferentes no son iguales."""
        id1 = UserId(uuid4())
        id2 = UserId(uuid4())
        assert id1 != id2
