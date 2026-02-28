from django.conf import settings

from ...domain.services.email_sender import EmailSender
from .console_email_sender import ConsoleEmailSender
from .sendgrid_email_sender import SendGridEmailSender


def get_email_sender() -> EmailSender:
    """
    Retorna el sender adecuado según el entorno:
    - Si SENDGRID_API_KEY está configurada → SendGrid (producción)
    - Si no → Consola (desarrollo)
    """
    api_key = getattr(settings, "SENDGRID_API_KEY", "")
    if api_key:
        return SendGridEmailSender()
    return ConsoleEmailSender()
