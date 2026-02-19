from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.logout_user import LogoutUser
from ...domain.exceptions import ExpiredTokenException, InvalidTokenException
from ...infrastructure.repositories.django_auth_session_repository import DjangoAuthSessionRepository
from ...infrastructure.services.jwt_token_provider import JwtTokenProvider
from ..serializers.login_serializer import LogoutRequestSerializer


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Cerrar sesion",
        request=LogoutRequestSerializer,
        responses={
            200: {"description": "Sesion cerrada"},
            401: {"description": "Token invalido"},
        },
        tags=["auth"],
    )
    def post(self, request):
        serializer = LogoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = LogoutUser(
            session_repository=DjangoAuthSessionRepository(),
            token_provider=JwtTokenProvider(),
        )

        try:
            use_case.execute(
                refresh_token=serializer.validated_data["refresh_token"],
            )
        except (InvalidTokenException, ExpiredTokenException) as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "Sesion cerrada exitosamente"}, status=status.HTTP_200_OK)
