from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Odds:
    """Value object para coutas de apuesta (maximo 2 decimales)"""

    value: Decimal

    def __post_init__(self):
        try:
            val = Decimal(str(self.value))
        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValueError("La couta no es un valor numerico valido") from e

        if val <= Decimal("1.00"):
            raise ValueError("La couta debe ser mayor a 1.00")

        exponent = val.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -2:
            raise ValueError("La couta no puede tener mas de 2 decimales")
