from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "src.apps.users"
    label = "users"

    def ready(self):
        # Registrar extensión de drf-spectacular para JwtAuthentication
        pass
