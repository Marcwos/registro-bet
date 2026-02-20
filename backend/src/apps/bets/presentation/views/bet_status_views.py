from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.use_cases.list_bet_statuses import ListBetStatuses
from ...infrastructure.repositories.django_bet_status_repository import DjangoBetStatusRepository
from ..serializers.bet_status_serializer import BetStatusResponseSerializer


class BetStatusListView(APIView):
    """Listar todos los estados de apuestas"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar estados de apuesta",
        description="Devuelve todos los estados posibles (pendiente, ganada, perdida, nula)",
        responses={200: BetStatusResponseSerializer(many=True)},
        tags=["catalogs"],
    )
    def get(self, request):
        repository = DjangoBetStatusRepository()
        use_case = ListBetStatuses(repository)
        statuses = use_case.execute()

        data = [{"id": s.id, "name": s.name, "code": s.code, "is_final": s.is_final} for s in statuses]
        serializer = BetStatusResponseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
