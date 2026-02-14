class DomainException(Exception):
    """Base para todas las excepciones de dominio"""

class UserAlreadyExistsException(DomainException):
    def __init__(self):
        super().__init__("El email ya esta registrado")
    
class InvalidCredentialsException(DomainException):
    def __init__(self):
        super().__init__("Credenciales invalidas")

class UserNotFoundException(DomainException):
    def __init__(self):
        super().__init__("Usuario no encontrado")