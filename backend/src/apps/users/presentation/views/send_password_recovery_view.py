from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.send_password_recovery import SendPasswordRecovery
from ...infrastructure.repositories.django_email_verification_repository import DjangoEmailVerificationRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.console_email_sender import ConsoleEmailSender
from ...infrastructure.services.random_verification_code_generator import RandomVerficationCodeGnerator
from ..serializers.verification_serializer import SendPasswordRecoverySerializer


class SendPasswordRecoveryView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Enviar codigo de recuperacion de contraseña",
        description="Envia un codigo de 6 digitos al email para recuperar la contraseña",
        request=SendPasswordRecoverySerializer,
        responses={
            200: {"description": "Si el email existe, se envio el codigo"},
        },
        tags=["recovery"],
    )
    def post(self, request):
        serializer = SendPasswordRecoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = SendPasswordRecovery(
            user_repository=DjangoUserRepository(),
            verification_repository=DjangoEmailVerificationRepository(),
            email_sender=ConsoleEmailSender(),
            code_generator=RandomVerficationCodeGnerator(),
        )

        use_case.execute(email=serializer.validated_data["email"])

        return Response(
            {"message": "Si el email esta registrado, recibiras un codigo de recuperacion"}, status=status.HTTP_200_OK
        )
