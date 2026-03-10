"""
Tests de dominio — Value Object: Email

¿Por qué testear value objects?
───────────────────────────────
Los value objects contienen reglas de negocio puras (validaciones de formato,
rangos, etc.). Son la parte más fácil y rápida de testear porque:
  - No tienen dependencias externas
  - No necesitan mocks
  - Son funciones puras: entrada → resultado/error

Estos tests son los MÁS RÁPIDOS de tu suite y los más valiosos porque
protegen las reglas de tu dominio.
"""

import pytest

from ...domain.value_objects.email import Email


class TestEmail:
    # ─── HAPPY PATH ────────────────────────────────────────────

    def test_create_valid_email(self):
        """Un email con formato correcto se crea sin errores."""
        email = Email("usuario@ejemplo.com")
        assert email.value == "usuario@ejemplo.com"

    def test_create_email_with_subdomain(self):
        """Emails con subdominios son válidos."""
        email = Email("user@mail.empresa.co")
        assert email.value == "user@mail.empresa.co"

    def test_create_email_with_dots_and_hyphens(self):
        """Emails con puntos y guiones en el nombre son válidos."""
        email = Email("mi.usuario-test@dominio.com")
        assert email.value == "mi.usuario-test@dominio.com"

    # ─── ERROR PATHS ───────────────────────────────────────────

    def test_email_without_at_raises_error(self):
        """Email sin @ es inválido."""
        with pytest.raises(ValueError, match="formato del email"):
            Email("usuarioejemplo.com")

    def test_email_without_domain_raises_error(self):
        """Email sin dominio después del @ es inválido."""
        with pytest.raises(ValueError, match="formato del email"):
            Email("usuario@")

    def test_email_without_tld_raises_error(self):
        """Email sin extensión (.com, .co, etc.) es inválido."""
        with pytest.raises(ValueError, match="formato del email"):
            Email("usuario@dominio")

    def test_empty_email_raises_error(self):
        """Email vacío es inválido."""
        with pytest.raises(ValueError, match="formato del email"):
            Email("")

    # ─── INMUTABILIDAD ─────────────────────────────────────────

    def test_email_is_immutable(self):
        """
        Email es frozen=True, por lo tanto no se puede modificar después
        de crearlo. Esto garantiza integridad del dato.
        """
        email = Email("test@ejemplo.com")
        with pytest.raises(AttributeError):
            email.value = "otro@email.com"

    # ─── NORMALIZACIÓN ─────────────────────────────────────────

    def test_email_is_normalized_to_lowercase(self):
        """El email siempre se almacena en minúsculas."""
        email = Email("Juan@Gmail.COM")
        assert email.value == "juan@gmail.com"

    def test_email_strips_whitespace(self):
        """Se eliminan espacios al inicio y final."""
        email = Email("  user@ejemplo.com  ")
        assert email.value == "user@ejemplo.com"
