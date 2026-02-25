from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.use_cases.change_bet_status import ChangeStatus
from ...application.use_cases.create_bet import CreateBet
from ...application.use_cases.delete_bet import DeleteBet
from ...application.use_cases.get_bet import GetBet
from ...application.use_cases.list_user_bets import ListUserBets
from ...application.use_cases.update_bet import UpdateBet
from ...domain.exceptions import (
    BetAccessDeniedException,
    BetNotEditableException,
    BetNotFoundException,
    BetStatusNotFoundException,
    InvalidOddsException,
    InvalidProfitExpectedException,
    InvalidStakeAmountException,
)
from ...infrastructure.repositories.django_bet_repository import DjangoBetRepository
from ...infrastructure.repositories.django_bet_status_repository import DjangoBetStatusRepository
from ..serializers.bet_serializer import (
    BetResponseSerializer,
    ChangeBetStatusRequestSerializer,
    CreateBetRequestSerializer,
    UpdateBetRequestSerializer,
)


def _bet_to_response(bet):
    """Convierte un entidad Bet a diccionario serializable"""
    return {
        "id": bet.id,
        "user_id": bet.user_id,
        "title": bet.title,
        "stake_amount": bet.stake_amount.amount,
        "odds": bet.odds.value,
        "profit_expected": bet.profit_expected,
        "profit_final": bet.profit_final,
        "status_id": bet.status_id,
        "sport_id": bet.sport_id,
        "category_id": bet.category_id,
        "description": bet.description,
        "placed_at": bet.placed_at,
        "settled_at": bet.settled_at,
        "created_at": bet.created_at,
        "updated_at": bet.updated_at,
    }


class BetListCreateView(APIView):
    """Listar apuestas del usuario o crear un nueva"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar apuestas del usuario",
        description="Dvuelve todas las apuestas del usuario autenticado",
        responses={200: BetResponseSerializer(many=True)},
        tags=["bets"],
    )
    def get(self, request):
        user_id = UUID(str(request.user.id))
        repository = DjangoBetRepository()
        use_case = ListUserBets(repository)
        bets = use_case.execute(user_id=user_id)

        data = [_bet_to_response(b) for b in bets]
        serializer = BetResponseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Crear apuesta",
        description="Crea una apuesta para el usuario autenticado. Titulo autogenerado",
        request=CreateBetRequestSerializer,
        responses={
            201: BetResponseSerializer,
            400: {"description": "Datos invalidos (monto, couta)"},
        },
        tags=["bets"],
    )
    def post(self, request):
        serializer = CreateBetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = UUID(str(request.user.id))
        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        try:
            use_case = CreateBet(bet_repo, status_repo)
            bet = use_case.execute(user_id=user_id, **serializer.validated_data)
        except (InvalidStakeAmountException, InvalidOddsException, InvalidProfitExpectedException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except BetStatusNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(BetResponseSerializer(_bet_to_response(bet)).data, status=status.HTTP_201_CREATED)


class BetDetailView(APIView):
    """Obtener, actualizar o eliminar apuesta"""

    permission_classes = []

    @extend_schema(
        summary="Obtener apuesta",
        description="Devuelve una apuesta especifica del usuario autenticado",
        responses={
            200: BetResponseSerializer,
            403: {"description": "No tienes acceso a esta apuesta"},
            404: {"description": "Apuesta no encontrada"},
        },
        tags=["bets"],
    )
    def get(self, request, bet_id):
        user_id = UUID(str(request.user.id))
        repository = DjangoBetRepository()

        try:
            use_case = GetBet(repository)
            bet = use_case.execute(bet_id=bet_id, user_id=user_id)
        except BetNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BetAccessDeniedException as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(BetResponseSerializer(_bet_to_response(bet)).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Actualizar apuesta",
        description="Actualiza una apuesta. Pendientes se editan libremente; cerradas requieren confirm=true",
        request=UpdateBetRequestSerializer,
        responses={
            200: BetResponseSerializer,
            400: {"description": "Datos inválidos"},
            403: {"description": "No tienes acceso a esta apuesta"},
            404: {"description": "Apuesta no encontrada"},
            409: {"description": "Apuesta cerrada sin confirmación"},
        },
        tags=["bets"],
    )
    def patch(self, request, bet_id):
        serializer = UpdateBetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = UUID(str(request.user.id))
        validated = serializer.validated_data
        confirm = validated.pop("confirm", False)

        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        try:
            use_case = UpdateBet(bet_repo, status_repo)
            bet = use_case.execute(bet_id=bet_id, user_id=user_id, confirm=confirm, **validated)
        except BetNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BetAccessDeniedException as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except BetNotEditableException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except (InvalidStakeAmountException, InvalidOddsException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            BetResponseSerializer(_bet_to_response(bet)).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Eliminar apuesta",
        description="Elima una apuesta del usuario autenticado",
        responses={
            204: None,
            403: {"description": "No tienes acceso a esta apuesta"},
            404: {"description": "Apuesta no encontrada"},
        },
        tags=["bets"],
    )
    def delete(self, request, bet_id):
        user_id = UUID(str(request.user.id))
        repository = DjangoBetRepository()

        try:
            use_case = DeleteBet(repository)
            use_case.execute(bet_id=bet_id, user_id=user_id)
        except BetNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BetAccessDeniedException as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BetChangeStatusView(APIView):
    """Cambiar estado de una apuesta"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Cambiar de estado de apuesta",
        description="Cambia el estado de una apuesta (pending, won, lost, win). Se puede cambiar en cualquier momento",
        request=ChangeBetStatusRequestSerializer,
        responses={
            200: BetResponseSerializer,
            403: {"description": "No tienes acceso a esta apuesta"},
            404: {"description": "Apuesta o estado no encontrada"},
        },
        tags=["bets"],
    )
    def patch(self, request, bet_id):
        serializer = ChangeBetStatusRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = UUID(str(request.user.id))
        bet_repo = DjangoBetRepository()
        status_repo = DjangoBetStatusRepository()

        try:
            use_case = ChangeStatus(bet_repo, status_repo)
            bet = use_case.execute(bet_id=bet_id, user_id=user_id, **serializer.validated_data)
        except BetNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BetAccessDeniedException as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except BetStatusNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(BetResponseSerializer(_bet_to_response(bet)).data, status=status.HTTP_200_OK)
