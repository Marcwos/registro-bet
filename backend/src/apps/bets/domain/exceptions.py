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
