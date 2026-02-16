from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.refresh_token import RefreshToken
from ...domain.exceptions import ExpiredTokenException, InvalidTokenException, SessionRevokedException
from ...infrastructure.repositories.django_auth_session_repository import DjandoAuthSessionRepository
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ...infrastructure.services.jwt_token_provider import JwtTokenProvider
from ..serializers.login_serializer import RefreshRequestSerializer, RefreshResponseSerializers


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="Refrescar tokens",
        request=RefreshRequestSerializer,
        responses={200: RefreshResponseSerializers, 401: {"description": "Token invalido"}},
        tags=["auth"],
    )
    def post(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = RefreshToken(
            user_repository=DjangoUserRepository(),
            session_repository=DjandoAuthSessionRepository(),
            token_provider=JwtTokenProvider(),
        )

        try:
            result = use_case.execute(
                refresh_token=serializer.validated_data["refresh_token"],
            )
        except (InvalidTokenException, SessionRevokedException, ExpiredTokenException) as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        response_serializer = RefreshResponseSerializers(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
