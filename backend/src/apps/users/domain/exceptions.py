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


class ExpiredTokenException(DomainException):
    def __init__(self):
        super().__init__("El token ha expirado")


class InvalidTokenException(DomainException):
    def __init__(self):
        super().__init__("El token es invalido")


class SessionRevokedException(DomainException):
    def __init__(self):
        super().__init__("La sesion ha sido revocada")


class EmailNotVerifiedException(DomainException):
    def __init__(self):
        super().__init__("Debes verificar tu email antes de iniciar sesion")


class EmailAlreadyVerifiedException(DomainException):
    def __init__(self):
        super().__init__("El email ya esta verificado")


class InvalidVerificationCodeException(DomainException):
    def __init__(self):
        super().__init__("El codigo de verificacion es invalido")


class ExpiredVerificationCodeException(DomainException):
    def __init__(self):
        super().__init__("El codigo de verificacion ha expirado")


class VerificationCodeNotFoundException(DomainException):
    def __init__(self):
        super().__init__("Codigo de verificacion no encontrado")


class InvalidPasswordException(DomainException):
    def __init__(self):
        super().__init__("La contraseña actual es incorrecta")


class MaxAttemptExceededException(DomainException):
    def __init__(self):
        super().__init__("Has excedido el limite de intentos")


class CooldownNotExpiredException(DomainException):
    def __init__(self, seconds_remaining: int = 30):
        super().__init__(f"Debes esperar {seconds_remaining} segundos antes de solicitar otro codigo")
