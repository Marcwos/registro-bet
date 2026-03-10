import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)
        self._validate_format(self.value)

    @staticmethod
    def _validate_format(email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            raise ValueError("El formato del email no es valido")
