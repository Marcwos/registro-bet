from rest_framework import serializers


class SportRequestSerializer(serializers.Serializer):
    """Valida datos de entrada para crear/editar un deporte"""

    name = serializers.CharField(max_length=100)


class SportUpdateSerializer(serializers.Serializer):
    """Valida datos de entrada para actualizar un deporte"""

    name = serializers.CharField(max_length=100, required=False)
    is_active = serializers.BooleanField(required=False)


class SportResponseSerializer(serializers.Serializer):
    """Formatea la respuesta de un deporte"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()
