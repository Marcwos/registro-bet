from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...application.use_cases.create_bet_category import CreateBetCategory
from ...application.use_cases.list_bet_categories import ListBetCategories
from ...application.use_cases.update_bet_category import UpdateBetCategory
from ...domain.exceptions import BetCategoryAlreadyExistsException, BetCategoryNotFoundException
from ...infrastructure.repositories.django_bet_category_repository import DjangoBetCategoryRepository
from ..serializers.bet_category_serializer import (
    BetCategoryRequestSerializer,
    BetCategoryResponseSerializer,
    BetCategoryUpdateSerializer,
)


class BetCategoryListCreateView(APIView):
    """Listar categorias (autenticado) o crear una nueva (admin)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar categorias de apuesta",
        description="Devuelve todas las categorias disponibles",
        responses={200: BetCategoryResponseSerializer(many=True)},
        tags=["catalogs"],
    )
    def get(self, request):
        repository = DjangoBetCategoryRepository()
        use_case = ListBetCategories(repository)
        categories = use_case.execute()

        data = [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
        serializer = BetCategoryResponseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Crear categoría de apuesta",
        description="Crea una nueva categoría (solo admin)",
        request=BetCategoryRequestSerializer,
        responses={
            201: BetCategoryResponseSerializer,
            403: {"description": "No tienes permisos de administrador"},
            409: {"description": "Ya existe una categoría con ese nombre"},
        },
        tags=["catalogs"],
    )
    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {"error": "No tienes permisos de administrador"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BetCategoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repository = DjangoBetCategoryRepository()

        try:
            use_case = CreateBetCategory(repository)
            category = use_case.execute(
                name=serializer.validated_data["name"],
                description=serializer.validated_data.get("description", ""),
            )
        except BetCategoryAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        response_data = {"id": category.id, "name": category.name, "description": category.description}
        return Response(
            BetCategoryResponseSerializer(response_data).data,
            status=status.HTTP_201_CREATED,
        )


class BetCategoryDetailView(APIView):
    """Actualizar una categoría (solo admin)"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Actualizar categoría de apuesta",
        description="Actualiza nombre y/o descripción de una categoría (solo admin)",
        request=BetCategoryUpdateSerializer,
        responses={
            200: BetCategoryResponseSerializer,
            403: {"description": "No tienes permisos de administrador"},
            404: {"description": "Categoría no encontrada"},
            409: {"description": "Ya existe una categoría con ese nombre"},
        },
        tags=["catalogs"],
    )
    def patch(self, request, category_id):
        if request.user.role != "admin":
            return Response(
                {"error": "No tienes permisos de administrador"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = BetCategoryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repository = DjangoBetCategoryRepository()

        try:
            use_case = UpdateBetCategory(repository)
            category = use_case.execute(
                category_id=category_id,
                name=serializer.validated_data.get("name"),
                description=serializer.validated_data.get("description"),
            )
        except BetCategoryNotFoundException as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except BetCategoryAlreadyExistsException as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        response_data = {"id": category.id, "name": category.name, "description": category.description}
        return Response(
            BetCategoryResponseSerializer(response_data).data,
            status=status.HTTP_200_OK,
        )
