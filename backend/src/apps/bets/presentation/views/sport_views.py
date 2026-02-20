from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.use_cases.create_sport import CreateSport
from ...application.use_cases.list_sports import ListSports
from ...application.use_cases.update_sport import UpdateSport
from ...domain.exceptions import SportAlreadyExistsException, SportNotFoundException
from ...infrastructure.repositories.django_sport_repository import DjangoSportRepository
from ..serializers.sport_serializer import (
    SportRequestSerializer,
    SportResponseSerializer,
    SportUpdateSerializer,
)


class SportListCreateView(APIView):
    """Listar todos los deportes (autenticado) o crear uno nuevo (admin)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar deportes",
        description="Deevuelve todos los deportes disponibles",
        responses={200: SportResponseSerializer(many=True)},
        tags=["catalogs"],
    )
    def get(self, request):
        repository = DjangoSportRepository()
        user_case = ListSports(repository)
        sports = user_case.execute()

        data = [{"id": s.id, "name": s.name, "is_active": s.is_active} for s in sports]
        serializer = SportResponseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Crear deporte",
        description="Crea un nuevo deporte",
        request=SportRequestSerializer,
        responses={
            201: SportResponseSerializer,
            403: {"description": "No tienes permisos de administrados"},
            409: {"description": "Ya existe un deporte con ese nombre"},
        },
        tags=["catalogs"],
    )
    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {"error": "No tienes permisos de administrador"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repository = DjangoSportRepository()

        try:
            use_case = CreateSport(repository)
            sport = use_case.execute(name=serializer.validated_data["name"])
        except SportAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        response_data = {"id": sport.id, "name": sport.name, "is_active": sport.is_active}
        return Response(SportResponseSerializer(response_data).data, status=status.HTTP_201_CREATED)


class SportDetailView(APIView):
    """Actualizar un deporte (solo admin)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Actualizar deporte",
        description="Actualiza nombre y/o estado activo de un deporte (solo admin)",
        request=SportUpdateSerializer,
        responses={
            200: SportResponseSerializer,
            403: {"description": "No tienes permisos de administrador"},
            404: {"description": "Deporte no encontrado"},
            409: {"description": "Ya existe un deporte con ese nombre"},
        },
        tags=["catalogs"],
    )
    def patch(self, request, sport_id):
        if request.user.role != "admin":
            return Response(
                {"error": "No tienes permisos de administrador"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = SportUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repository = DjangoSportRepository()

        try:
            use_case = UpdateSport(repository)
            sport = use_case.execute(
                sport_id=sport_id,
                name=serializer.validated_data.get("name"),
                is_active=serializer.validated_data.get("is_active"),
            )
        except SportNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except SportAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        response_data = {"id": sport.id, "name": sport.name, "is_active": sport.is_active}
        return Response(
            SportResponseSerializer(response_data).data,
            status=status.HTTP_200_OK,
        )
