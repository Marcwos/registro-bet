from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        """Envia un email al destinatario.

        Args:
            to: Direccion de correo del destinatario.
            subject: Asunto del email.
            body: Contenido en texto plano (fallback).
            html_body: Contenido HTML opcional (preferido por los clientes de correo).
        """
