from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "src.apps.users"
    label = "users"

    def ready(self):
        # Importar extensión para que drf-spectacular la descubra automáticamente
        import src.apps.users.infrastructure.authentication.jwt_scheme  # noqa: F401
