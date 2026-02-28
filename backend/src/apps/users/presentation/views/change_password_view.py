from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.audit.infrastructure.repositories.django_audit_log_repository import DjangoAuditLogRepository
from src.apps.audit.infrastructure.services.default_audit_service import DefaultAuditService

from ...application.uses_cases.change_password import ChangePassword
from ...domain.exceptions import InvalidPasswordException, UserNotFoundException
from ...infrastructure.repositories.django_auth_session_repository import DjangoAuthSessionRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from ..serializers.verification_serializer import ChangePasswordRequestSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cambiar contraseña",
        description="Cambia la ontraseña del usuario autenticado. Invalida todas las sessiones activas",
        request=ChangePasswordRequestSerializer,
        responses={
            200: {"description": "Contraseña cambiada exitosamente"},
            400: {"description": "Contraseña actual incorrecta"},
            404: {"description": "Usuario no encontrado"},
        },
        tags=["users"],
    )
    def post(self, request):
        serializer = ChangePasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = ChangePassword(
            user_repository=DjangoUserRepository(),
            session_repository=DjangoAuthSessionRepository(),
            password_hasher=BcryptPasswordHasher(),
            audit_service=DefaultAuditService(DjangoAuditLogRepository()),
        )
        try:
            use_case.execute(
                user_id=request.user.id,
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except UserNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InvalidPasswordException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Contraseña cambiada exitosamente"}, status=status.HTTP_200_OK)
