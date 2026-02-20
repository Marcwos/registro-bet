from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JwtAuthenticationScheme(OpenApiAuthenticationExtension):
    """Registra JwtAuthentication en drf-spectacular como Bearer JWT."""

    target_class = "src.apps.users.infrastructure.authentication.jwt_authentication.JwtAuthentication"
    name = "JwtAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
