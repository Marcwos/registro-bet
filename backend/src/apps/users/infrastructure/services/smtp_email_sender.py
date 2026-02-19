from django.core.mail import send_mail

from ...domain.services.email_sender import EmailSender


class SmtpEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str) -> None:
        send_mail(
            subject=subject,
            message=body,
            from_email=None,
            recipient_list=[to],
            fail_silently=False,
        )
