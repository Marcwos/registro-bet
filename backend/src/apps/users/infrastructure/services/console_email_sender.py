from ...domain.services.email_sender import EmailSender


class ConsoleEmailSender(EmailSender):
    def send(self, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        print(f"\n{'=' * 50}")
        print(f"EMAIL TO: {to}")
        print(f"SUBJECT: {subject}")
        print(f"BODY: {body}")
        if html_body:
            print(f"HTML: (incluido, {len(html_body)} chars)")
        print(f"{'=' * 50}\n")
