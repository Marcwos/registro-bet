from django.conf import settings

from ...domain.services.email_sender import EmailSender
from .console_email_sender import ConsoleEmailSender
from .sendgrid_email_sender import SendGridEmailSender
from .smtp_email_sender import SmtpEmailSender


def get_email_sender() -> EmailSender:
    """
    Retorna el sender adecuado segun EMAIL_PROVIDER:
    - "smtp"     → Gmail SMTP (recomendado mientras no haya dominio propio)
    - "sendgrid" → SendGrid API (para cuando tengas dominio verificado)
    - "console"  → Imprime en consola (desarrollo local)
    """
    provider = getattr(settings, "EMAIL_PROVIDER", "console").lower()

    if provider == "smtp":
        return SmtpEmailSender()
    if provider == "sendgrid":
        return SendGridEmailSender()
    return ConsoleEmailSender()
