from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.audit.infrastructure.repositories.django_audit_log_repository import DjangoAuditLogRepository
from src.apps.audit.infrastructure.services.default_audit_service import DefaultAuditService

from ...application.uses_cases.login_user import LoginUser
from ...domain.exceptions import EmailNotVerifiedException, InvalidCredentialsException
from ...infrastructure.repositories.django_auth_session_repository import DjangoAuthSessionRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from ...infrastructure.services.jwt_token_provider import JwtTokenProvider
from ..serializers.login_serializer import LoginRequestSerializer, LoginResponseSerializer


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Iniciar sesion",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer, 401: {"description": "Credenciales invalidas"}},
        tags=["auth"],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = LoginUser(
            user_repository=DjangoUserRepository(),
            session_repository=DjangoAuthSessionRepository(),
            password_hasher=BcryptPasswordHasher(),
            token_provider=JwtTokenProvider(),
            audit_service=DefaultAuditService(DjangoAuditLogRepository()),
        )

        try:
            result = use_case.execute(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                ip_address=request.META.get("REMOTE_ADDR", "127.0.0.1"),
            )
        except InvalidCredentialsException as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except EmailNotVerifiedException as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        response_serializer = LoginResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
