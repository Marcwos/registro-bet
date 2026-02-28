from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.bets.infrastructure.repositories.django_bet_repository import DjangoBetRepository
from src.apps.users.infrastructure.authentication.permissions import IsAdmin
from src.apps.users.infrastructure.repositories.django_user_repository import DjangoUserRepository

from ...application.use_cases.get_admin_stats import GetAdminStats
from ...infrastructure.repositories.django_audit_log_repository import DjangoAuditLogRepository
from ..serializers.admin_stats_serializer import AdminStatsResponseSerializer


class AdminStatsView(APIView):
    """Metricas agregadas del sistema (solo admin)"""

    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Estadisticas de administrador",
        description="Devuelve metricas agregadas: total usuarios, apuestas, eventos de auditoria",
        responses={
            200: AdminStatsResponseSerializer,
            403: {"description": "No tienes permisos de administrador"},
        },
        tags=["admin"],
    )
    def get(self, request):
        use_case = GetAdminStats(
            user_repository=DjangoUserRepository(),
            bet_repository=DjangoBetRepository(),
            audit_log_repository=DjangoAuditLogRepository(),
        )
        result = use_case.execute()
        serializer = AdminStatsResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
