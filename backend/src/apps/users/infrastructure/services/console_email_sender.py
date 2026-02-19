from ...domain.services.email_sender import EmailSender


class ConsoleEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str) -> None:
        print(f"\n{'=' * 50}")
        print(f"EMAIL TO: {to}")
        print(f"SUBJECT: {subject}")
        print(f"BODY: {body}")
        print(f"{'=' * 50}\n")
