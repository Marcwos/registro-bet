from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.users.infrastructure.authentication.permissions import IsAdmin

from ...application.use_cases.list_audit_logs import ListAuditLogs
from ...infrastructure.repositories.django_audit_log_repository import DjangoAuditLogRepository
from ..serializers.audit_log_serializer import AuditLogListResponseSerializer


class AuditLogListView(APIView):
    """Listado de eventos de auditoria paginados (solo admin)"""

    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Listar eventos de auditoria",
        description="Devuelve los eventos de auditoria paginados. Solo accesible por admin",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Cantidad de registros por pagina (default: 50)",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Desplazamiento para paginacion (default: 0)",
                required=False,
            ),
        ],
        responses={
            200: AuditLogListResponseSerializer,
            403: {"description": "No tienes permisos de administrador"},
        },
        tags=["admin"],
    )
    def get(self, request):
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))

        use_case = ListAuditLogs(audit_log_repository=DjangoAuditLogRepository())
        result = use_case.execute(limit=limit, offset=offset)

        # Convertir entidades a dicts para el serializer
        items_data = [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "metadata": log.metadata,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in result["items"]
        ]

        serializer = AuditLogListResponseSerializer({"items": items_data, "total": result["total"]})
        return Response(serializer.data, status=status.HTTP_200_OK)
