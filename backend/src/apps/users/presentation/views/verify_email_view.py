from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.verify_email import VerifyEmail
from ...domain.exceptions import (
    EmailAlreadyVerifiedException,
    ExpiredVerificationCodeException,
    InvalidVerificationCodeException,
    MaxAttemptExceededException,
    UserNotFoundException,
    VerificationCodeNotFoundException,
)
from ...infrastructure.repositories.django_email_verification_repository import DjangoEmailVerificationRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ..serializers.verification_serializer import VerifyEmailRequestSerializer


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Verificar email con codigo",
        description="Valida el codigo de 6 digitos y marca email como verificado",
        request=VerifyEmailRequestSerializer,
        responses={
            200: {"description": "Email verificado exitosamente"},
            400: {"description": "Codigo invalido, expirdado o ya usado"},
            404: {"description": "Usuario no encontrado"},
            429: {"description": "Limite de intentos excedido"},
        },
        tags=["verification"],
    )
    def post(self, request):
        serializer = VerifyEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = VerifyEmail(
            user_repository=DjangoUserRepository(),
            verification_repository=DjangoEmailVerificationRepository(),
        )

        try:
            use_case.execute(user_id=serializer.validated_data["user_id"], code=serializer.validated_data["code"])
        except UserNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EmailAlreadyVerifiedException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except MaxAttemptExceededException as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except InvalidVerificationCodeException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ExpiredVerificationCodeException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except VerificationCodeNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Email verificado exitosamente"}, status=status.HTTP_200_OK)
