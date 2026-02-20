from rest_framework import serializers


class BetCategoryRequestSerializer(serializers.Serializer):
    """Valida datos de entrada para crear/editar una categoria"""

    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, default="", allow_blank=True)


class BetCategoryUpdateSerializer(serializers.Serializer):
    """Valida datos de entrada para actualizar una categoria"""

    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class BetCategoryResponseSerializer(serializers.Serializer):
    """Formatea la respuesta de una categoria"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
