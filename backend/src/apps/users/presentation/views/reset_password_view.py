from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.reset_password import ResetPassword
from ...domain.exceptions import (
    ExpiredVerificationCodeException,
    InvalidVerificationCodeException,
    MaxAttemptExceededException,
    UserNotFoundException,
    VerificationCodeNotFoundException,
)
from ...infrastructure.repositories.django_auth_session_repository import DjangoAuthSessionRepository
from ...infrastructure.repositories.django_email_verification_repository import DjangoEmailVerificationRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from ..serializers.verification_serializer import ResetPasswordRequestSerializer


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Restablecer contraseña con codigo",
        description="Valida el codigo de recuperacion y establece la contraseña. Invalida todas la sessiones activas",
        request=ResetPasswordRequestSerializer,
        responses={
            200: {"description": "Contraseña restablecida exitosamente"},
            400: {"description": "Codigo invalido o expirado"},
            404: {"description": "Usuario no encontrado"},
            429: {"description": "Limite de intentos excedido"},
        },
        tags=["recovery"],
    )
    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = ResetPassword(
            user_repository=DjangoUserRepository(),
            verification_repository=DjangoEmailVerificationRepository(),
            session_repository=DjangoAuthSessionRepository(),
            password_hasher=BcryptPasswordHasher(),
        )

        try:
            use_case.execute(
                email=serializer.validated_data["email"],
                code=serializer.validated_data["code"],
                new_password=serializer.validated_data["new_password"],
            )
        except UserNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except MaxAttemptExceededException as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except (
            InvalidVerificationCodeException,
            ExpiredVerificationCodeException,
            VerificationCodeNotFoundException,
        ) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Contraseña restablecida exitosamente"}, status=status.HTTP_200_OK)
