from rest_framework import serializers


class BetStatusResponseSerializer(serializers.Serializer):
    """Formatea la respuesta de un estado de apuesta"""

    id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    is_final = serializers.BooleanField()
