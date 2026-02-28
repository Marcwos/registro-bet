from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.send_verification_email import SendVerificationEmail
from ...domain.exceptions import CooldownNotExpiredException, EmailAlreadyVerifiedException, UserNotFoundException
from ...infrastructure.repositories.django_email_verification_repository import DjangoEmailVerificationRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.email_sender_factory import get_email_sender
from ...infrastructure.services.random_verification_code_generator import RandomVerficationCodeGnerator
from ..serializers.verification_serializer import SendVerificationRequestSerializer


class SendVerificationEmailView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Enviar codigo de verificacion de email",
        description="Genera y envio de codigo de 6 digitos al email del usuario",
        request=SendVerificationRequestSerializer,
        responses={
            200: {"description": "Codigo enviado exitosamente"},
            400: {"description": "El email ya esta verificado"},
            404: {"description": "Usuario no encontrado"},
            429: {"description": "Debes esperar antes de solicitar otro codigo"},
        },
        tags=["verification"],
    )
    def post(self, request):
        serializer = SendVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = SendVerificationEmail(
            user_repository=DjangoUserRepository(),
            verification_repository=DjangoEmailVerificationRepository(),
            email_sender=get_email_sender(),
            code_generator=RandomVerficationCodeGnerator(),
        )
        try:
            use_case.execute(user_id=serializer.validated_data["user_id"])
        except UserNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EmailAlreadyVerifiedException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except CooldownNotExpiredException as e:
            return Response({"error": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({"message": "Código de verificación enviado"}, status=status.HTTP_200_OK)
