from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Money:
    """Value objets para montos monetarios de USB"""

    amount: Decimal

    def __post_init__(self):
        try:
            value = Decimal(str(self.amount))
        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValueError("El monto no es un valor numerico valido") from e

        if value <= 0:
            raise ValueError("El monto debe ser mayor a 0")

        exponent = value.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("El monto no puede tener mas de 2 decimales")
