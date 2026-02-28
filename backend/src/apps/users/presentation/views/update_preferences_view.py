from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.uses_cases.update_user_preferences import UpdateUserPreferences
from ...domain.exceptions import UserNotFoundException
from ...infrastructure.repositories.django_user_repository import DjangoUserRepository
from ..serializers.preferences_serializer import (
    PreferencesResponseSerializer,
    UpdatePreferencesSerializer,
)


class UpdatePreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Actualizar preferencias del usuario",
        description="Permite cambiar tema (light/dark) y zona horaria",
        request=UpdatePreferencesSerializer,
        responses={200: PreferencesResponseSerializer},
        tags=["users"],
    )
    def patch(self, request):
        serializer = UpdatePreferencesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        use_case = UpdateUserPreferences(
            user_repository=DjangoUserRepository(),
        )

        try:
            result = use_case.execute(
                user_id=UUID(str(request.user.id)),
                theme_preference=serializer.validated_data.get("theme_preference"),
                timezone=serializer.validated_data.get("timezone"),
            )
        except UserNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        response = PreferencesResponseSerializer(result)
        return Response(response.data, status=status.HTTP_200_OK)
