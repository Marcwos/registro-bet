from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ...domain.services.email_sender import EmailSender


class SendGridEmailSender(EmailSender):
    """Envía emails reales usando la API de SendGrid."""

    def send(self, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to,
            subject=subject,
            plain_text_content=body,
            html_content=html_body or None,
        )

        client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        client.send(message)
