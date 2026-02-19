import secrets

from ...domain.services.verification_code_generator import VerificationCodeGenerator


class RandomVerficationCodeGnerator(VerificationCodeGenerator):
    def generate(self) -> str:
        """Genera un codigo numerico de 6 digitos"""
        return f"{secrets.randbelow(1000000):06d}"
