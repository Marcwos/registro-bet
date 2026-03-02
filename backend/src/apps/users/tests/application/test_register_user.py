"""
Tests unitarios para RegisterUser use case.

¿Qué es un test unitario?
─────────────────────────
Un test unitario prueba UNA SOLA unidad de código (aquí: un caso de uso)
de forma AISLADA, sin base de datos, sin red, sin archivos.

¿Cómo logramos el aislamiento?
──────────────────────────────
Usando `unittest.mock.Mock`. Mock crea objetos falsos que simulan las
interfaces (UserRepository, PasswordHasher, etc.) y nos permiten:
  1. Programar qué devuelven:  mock.method.return_value = algo
  2. Programar que lancen error: mock.method.side_effect = Exception()
  3. Verificar que se llamaron:  mock.method.assert_called_once()

Estructura de cada test: ARRANGE → ACT → ASSERT
─────────────────────────────────────────────────
  ARRANGE: Crear los mocks, configurar su comportamiento, instanciar el caso de uso.
  ACT:     Llamar a use_case.execute(...) con los datos de prueba.
  ASSERT:  Verificar el resultado (return value) y los efectos (llamadas a mocks).
"""

from unittest.mock import Mock

import pytest

from ...application.uses_cases.register_user import RegisterUser
from ...domain.entities.user import User
from ...domain.exceptions import UserAlreadyExistsException
from ...domain.repositories.user_repository import UserRepository
from ...domain.services.password_hasher import PasswordHasher


class TestRegisterUser:
    """
    Agrupamos los tests en una clase para organizarlos por caso de uso.
    Cada método test_* es un escenario diferente.
    """

    # ─── Helpers ────────────────────────────────────────────────
    # setup_method se ejecuta ANTES de cada test automáticamente.
    # Aquí creamos los mocks frescos para que cada test sea independiente.

    def setup_method(self):
        """
        Se ejecuta antes de CADA test. Crea mocks frescos.

        Mock(spec=UserRepository) crea un objeto que:
          - Tiene los mismos métodos que UserRepository (save, get_by_email, etc.)
          - Lanza error si llamas a un método que NO existe en la interfaz
          - NO ejecuta lógica real (todo es simulado)
        """
        self.user_repo = Mock(spec=UserRepository)
        self.password_hasher = Mock(spec=PasswordHasher)

        # Instanciamos el caso de uso con las dependencias FALSAS
        self.use_case = RegisterUser(
            user_repository=self.user_repo,
            password_hasher=self.password_hasher,
        )

    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_register_user_successfully(self):
        """
        Escenario: El usuario se registra correctamente.
        Condicion: El email NO existe en el sistema.
        Resultado esperado: Se crea un User y se guarda en el repositorio.
        """
        # ARRANGE ─────────────────────────────────────────────
        # Configuramos el mock: "cuando busquen este email, devuelve None (no existe)"
        self.user_repo.get_by_email.return_value = None
        # Configuramos el hasher: "cuando hasheen un password, devuelve este string"
        self.password_hasher.hash.return_value = "hashed_abc123"

        # ACT ─────────────────────────────────────────────────
        # Ejecutamos el caso de uso como si fuera una petición real
        result = self.use_case.execute(
            email="nuevo@example.com",
            password="MiPassword123",
        )

        # ASSERT ──────────────────────────────────────────────
        # 1. Verificar que el resultado es un User con los datos correctos
        assert isinstance(result, User)
        assert result.email.value == "nuevo@example.com"
        assert result.password_hash == "hashed_abc123"
        assert result.is_email_verified is False
        assert result.role.value == "user"

        # 2. Verificar que se llamó a repo.save() exactamente 1 vez
        #    assert_called_once() falla si se llamó 0 o 2+ veces
        self.user_repo.save.assert_called_once()

        # 3. Verificar que el password se hasheó con el password original
        self.password_hasher.hash.assert_called_once_with("MiPassword123")

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_register_fails_when_email_already_exists(self):
        """
        Escenario: El email ya está registrado y verificado.
        Resultado esperado: Se lanza UserAlreadyExistsException y NO se guarda nada.
        """
        # ARRANGE: simular usuario verificado existente
        existing_user = Mock(spec=User)
        existing_user.is_email_verified = True
        self.user_repo.get_by_email.return_value = existing_user

        # ACT + ASSERT ────────────────────────────────────────
        # pytest.raises() verifica que se lance EXACTAMENTE esta excepción
        with pytest.raises(UserAlreadyExistsException):
            self.use_case.execute("existente@example.com", "123456")

        # Verificar que NUNCA se intentó guardar (el flujo se cortó antes)
        self.user_repo.save.assert_not_called()

    def test_register_fails_with_invalid_email_format(self):
        """
        Escenario: El email tiene un formato inválido.
        Resultado esperado: El Value Object Email lanza ValueError.

        Nota: Esta validación viene del Value Object Email, no del caso de uso.
        Pero el test verifica que el caso de uso propaga el error correctamente.
        """
        # ARRANGE
        self.user_repo.get_by_email.return_value = None

        # ACT + ASSERT
        with pytest.raises(ValueError, match="formato del email"):
            self.use_case.execute("email-invalido", "123456")

        # No se debe guardar nada
        self.user_repo.save.assert_not_called()
