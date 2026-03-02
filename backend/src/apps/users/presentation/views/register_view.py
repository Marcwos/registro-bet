import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.audit.infrastructure.repositories.django_audit_log_repository import DjangoAuditLogRepository
from src.apps.audit.infrastructure.services.default_audit_service import DefaultAuditService

from ...application.uses_cases.register_user import RegisterUser
from ...application.uses_cases.send_verification_email import SendVerificationEmail
from ...domain.exceptions import UserAlreadyExistsException
from ...infrastructure.repositories.django_email_verification_repository import DjangoEmailVerificationRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from ...infrastructure.services.email_sender_factory import get_email_sender
from ...infrastructure.services.random_verification_code_generator import RandomVerficationCodeGnerator
from ..serializers.register_serializer import RegisterRequestSerializer, RegisterResponseSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    """ Endpoint para registrar un nuevo usuario

    Flujo:
    1. El serializers valida email y password
    2. Se inyectan las dependencias (repository + hasher)
    3. Se ejecuta el use case
    4. Se formatea la respuesta
    """

    @extend_schema(
        summary="Registrar usuario",
        description="Crea un nuevo usuario con email y contraseña",
        request=RegisterRequestSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: {"description": "Datos invalidos"},
            409: {"description": "El email ya esta registrado"},
        },
        tags=["users"],
    )
    def post(self, request):
        # 1. Validar datos de entrada
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Inyectar dependencias
        repository = DjangoUserRepository()
        hasher = BcryptPasswordHasher()
        audit_service = DefaultAuditService(DjangoAuditLogRepository())

        try:
            # 3. Ejecutar use case
            use_case = RegisterUser(repository, hasher, audit_service=audit_service)
            user = use_case.execute(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except UserAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Enviar email de verificacion automaticamente
        #    EMAIL_TIMEOUT en settings protege contra conexiones SMTP colgadas
        try:
            send_email_use_case = SendVerificationEmail(
                user_repository=repository,
                verification_repository=DjangoEmailVerificationRepository(),
                email_sender=get_email_sender(),
                code_generator=RandomVerficationCodeGnerator(),
            )
            send_email_use_case.execute(user_id=str(user.id.value))
        except Exception:
            # Si falla el envio (timeout, SMTP error, etc.), no bloqueamos el registro.
            # El usuario puede reenviar desde la pantalla de verificacion.
            logger.exception("Error al enviar email de verificacion durante el registro")

        # 5. Formatear respuesta
        response_data = {
            "id": user.id.value,
            "email": user.email.value,
            "role": user.role.value,
            "is_email_verified": user.is_email_verified,
            "created_at": user.created_at,
        }
        response_serializer = RegisterResponseSerializer(response_data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
