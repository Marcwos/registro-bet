class BetsDomainException(Exception):
    """Base para excepciones del dominio de apuestas"""


class SportAlreadyExistsException(BetsDomainException):
    def __init__(self):
        super().__init__("Ya existe un deporte con ese nombre")


class SportNotFoundException(BetsDomainException):
    def __init__(self):
        super().__init__("Deporte no encontrado")


class BetCategoryAlreadyExistsException(BetsDomainException):
    def __init__(self):
        super().__init__("Ya existe una catgeoria con ese nomnre")


class BetCategoryNotFoundException(BetsDomainException):
    def __init__(self):
        super().__init__("Categoría no encontrada")


class BetStatusNotFoundException(BetsDomainException):
    def __init__(self):
        super().__init__("Estado de apuesta no encontrado")


class BetNotFoundException(BetsDomainException):
    def __init__(self):
        super().__init__("Apuesta no encontradda")


class BetAccessDeniedException(BetsDomainException):
    def __init__(self):
        super().__init__("No tienes acceso a esta apuesta")


class BetNotEditableException(BetsDomainException):
    def __init__(self):
        super().__init__(
            "La apuesta no es editable sin confirmacion. Envia confirm=true para editar una apuesta cerrada"
        )


class InvalidStakeAmountException(BetsDomainException):
    def __init__(self, detail: str = ""):
        msg = "Monto de apuesta invalido"
        if detail:
            msg = f"{msg}: {detail}"
        super().__init__(msg)


class InvalidOddsException(BetsDomainException):
    def __init__(self, detail: str = ""):
        msg = "Couta invalida"
        if detail:
            msg = f"{msg}: {detail}"
        super().__init__(msg)


class InvalidProfitExpectedException(BetsDomainException):
    def __init__(self, detail: str = ""):
        msg = "Ganancia esperada invalida"
        if detail:
            msg = f"{msg}: {detail}"
        super().__init__(msg)


class InvalidBetTypeException(BetsDomainException):
    def __init__(self):
        super().__init__("Una apuesta no puede ser Bono (freebet) y tener Bonificación (boost) al mismo tiempo")
