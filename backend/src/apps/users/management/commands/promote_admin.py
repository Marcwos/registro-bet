from django.core.management.base import BaseCommand, CommandError

from ...infrastructure.models.user_model import UserModel


class Command(BaseCommand):
    help = "Promueve un usuario existente a rol admin"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email del usuario a promover")

    def handle(self, *args, **options):
        email = options["email"]

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist as e:
            raise CommandError(f"No existe un usuario con email: {email}") from e

        if user.role == "admin":
            self.stdout.write(self.style.WARNING(f"{email} ya es admin"))
            return

        user.role = "admin"
        user.save(update_fields=["role"])

        self.stdout.write(self.style.SUCCESS(f"{email} ahora es admin"))
