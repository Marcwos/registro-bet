from django.core.mail import send_mail

from ...domain.services.email_sender import EmailSender


class SmtpEmailSender(EmailSender):
    """Envia emails usando el backend SMTP configurado en Django (ej. Gmail)."""

    def send(self, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        send_mail(
            subject=subject,
            message=body,
            from_email=None,  # usa DEFAULT_FROM_EMAIL de settings
            recipient_list=[to],
            html_message=html_body,
            fail_silently=False,
        )
