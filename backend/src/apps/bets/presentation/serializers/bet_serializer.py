from rest_framework import serializers


class CreateBetRequestSerializer(serializers.Serializer):
    """Valida datos de entrada para crear una apuesta"""

    stake_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    odds = serializers.DecimalField(max_digits=8, decimal_places=2)
    profit_expected = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_final = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    placed_at = serializers.DateTimeField(required=False)
    sport_id = serializers.UUIDField(required=False, allow_null=True)
    category_id = serializers.UUIDField(required=False, allow_null=True)
    description = serializers.CharField(required=False, default="", allow_blank=True)


class UpdateBetRequestSerializer(serializers.Serializer):
    """Valida datos de entrada para actualizar una apuesta"""

    stake_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    odds = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    profit_expected = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    profit_final = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    placed_at = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    confirm = serializers.BooleanField(required=False, default=False)


class ChangeBetStatusRequestSerializer(serializers.Serializer):
    """Valida datos para cambiar el estado de una apuesta"""

    status_code = serializers.CharField(max_length=20)
    profit_final = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)


class BetResponseSerializer(serializers.Serializer):
    """Formatea la respuesta de una apuesta"""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    title = serializers.CharField()
    stake_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    odds = serializers.DecimalField(max_digits=8, decimal_places=2)
    profit_expected = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_final = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    status_id = serializers.UUIDField()
    sport_id = serializers.UUIDField(allow_null=True)
    category_id = serializers.UUIDField(allow_null=True)
    description = serializers.CharField()
    placed_at = serializers.DateTimeField()
    settled_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
