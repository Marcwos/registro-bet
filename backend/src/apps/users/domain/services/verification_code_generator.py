from abc import ABC, abstractmethod


class VerificationCodeGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        """Genera un codigo de verificacion de 6 digitos"""
