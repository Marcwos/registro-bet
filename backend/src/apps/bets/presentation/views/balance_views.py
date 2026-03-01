from datetime import date
from uuid import UUID

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.use_cases.get_bet_history import GetBetHistory
from ...application.use_cases.get_daily_balance import GetDailyBalance
from ...application.use_cases.get_total_balance import GetTotalBalance
from ...domain.services.tz_utils import parse_tz_params
from ...infrastructure.repositories.django_bet_repository import DjangoBetRepository
from ...infrastructure.repositories.django_bet_status_repository import (
    DjangoBetStatusRepository,
)
from ..serializers.balance_serializer import (
    BetHistoryQuerySerializer,
    BetHistorySummarySerializer,
    DailyBalanceQuerySerializer,
    DailyBalanceResponseSerializer,
    TotalBalanceResponseSerializer,
)
from ..serializers.bet_serializer import BetResponseSerializer
from ..views.bet_views import _bet_to_response


class DailyBalanceView(APIView):
    """Balance del día: ganancias, pérdidas, profit neto"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Balance diario",
        description="Calcula el balance de un día específico desde datos reales",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Fecha (YYYY-MM-DD). Si no se envía, usa hoy",
                required=False,
            ),
        ],
        responses={200: DailyBalanceResponseSerializer},
        tags=["statistics"],
    )
    def get(self, request):
        user_id = UUID(str(request.user.id))

        # Si no se envía fecha, usar hoy
        if "date" in request.query_params:
            query_serializer = DailyBalanceQuerySerializer(data=request.query_params)
            query_serializer.is_valid(raise_exception=True)
            target_date = query_serializer.validated_data["date"]
        else:
            target_date = date.today()

        # Timezone del cliente (IANA name o offset en minutos)
        try:
            tz_params = parse_tz_params(request.query_params)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        use_case = GetDailyBalance(bet_repo, status_repo)
        balance = use_case.execute(user_id=user_id, tarjet_date=target_date, **tz_params)

        serializer = DailyBalanceResponseSerializer(
            {
                "target_date": balance.tarjet_date,
                "total_staked": balance.total_staked,
                "total_won": balance.total_won,
                "total_lost": balance.total_lost,
                "total_return": balance.total_return,
                "net_profit": balance.net_profit,
                "bet_count": balance.bet_count,
                "won_count": balance.won_count,
                "lost_count": balance.lost_count,
                "void_count": balance.void_count,
                "pending_count": balance.pending_count,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TotalBalanceView(APIView):
    """Balance total histórico del usuario"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Balance total",
        description="Calcula el balance histórico total acumulado del usuario",
        responses={200: TotalBalanceResponseSerializer},
        tags=["statistics"],
    )
    def get(self, request):
        user_id = UUID(str(request.user.id))

        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        use_case = GetTotalBalance(bet_repo, status_repo)
        balance = use_case.execute(user_id=user_id)

        serializer = TotalBalanceResponseSerializer(
            {
                "total_staked": balance.total_staked,
                "total_won": balance.total_won,
                "total_lost": balance.total_lost,
                "total_return": balance.total_return,
                "net_profit": balance.net_profit,
                "bet_count": balance.bet_count,
                "won_count": balance.won_count,
                "lost_count": balance.lost_count,
                "void_count": balance.void_count,
                "pending_count": balance.pending_count,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BetHistoryView(APIView):
    """Historial de apuestas filtrado por rango de fechas"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Historial de apuestas",
        description="Devuelve apuestas + resumen dentro de un rango de fechas",
        parameters=[
            OpenApiParameter(
                name="start_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Fecha inicio (YYYY-MM-DD)",
                required=True,
            ),
            OpenApiParameter(
                name="end_date",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Fecha fin (YYYY-MM-DD)",
                required=True,
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "summary": {"$ref": "#/components/schemas/BetHistorySummary"},
                    "bets": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/BetResponse"},
                    },
                },
            }
        },
        tags=["statistics"],
    )
    def get(self, request):
        query_serializer = BetHistoryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        user_id = UUID(str(request.user.id))
        start_date = query_serializer.validated_data["start_date"]
        end_date = query_serializer.validated_data["end_date"]

        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        use_case = GetBetHistory(bet_repo, status_repo)
        try:
            tz_params = parse_tz_params(request.query_params)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        bets, summary = use_case.execute(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            **tz_params,
        )

        bets_data = [_bet_to_response(b) for b in bets]

        return Response(
            {
                "summary": BetHistorySummarySerializer(
                    {
                        "start_date": summary.start_date,
                        "end_date": summary.end_date,
                        "total_staked": summary.total_staked,
                        "total_won": summary.total_won,
                        "total_lost": summary.total_lost,
                        "total_return": summary.total_return,
                        "net_profit": summary.net_profit,
                        "bet_count": summary.bet_count,
                        "won_count": summary.won_count,
                        "lost_count": summary.lost_count,
                        "void_count": summary.void_count,
                        "pending_count": summary.pending_count,
                    }
                ).data,
                "bets": BetResponseSerializer(bets_data, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
