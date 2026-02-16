from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.register_user import RegisterUser
from ...domain.exceptions import UserAlreadyExistsException
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from ..serializers.register_serializer import RegisterRequestSerializer, RegisterResponseSerializer


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

        try:
            # 3. Ejecutar use case
            use_case = RegisterUser(repository, hasher)
            user = use_case.execute(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except UserAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Formatear respuesta
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
