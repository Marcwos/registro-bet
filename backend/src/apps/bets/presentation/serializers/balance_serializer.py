from rest_framework import serializers


class DailyBalanceResponseSerializer(serializers.Serializer):
    """Respuesta del balance diario"""

    target_date = serializers.DateField()
    total_staked = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_won = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_lost = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    bet_count = serializers.IntegerField()
    won_count = serializers.IntegerField()
    lost_count = serializers.IntegerField()
    void_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()


class TotalBalanceResponseSerializer(serializers.Serializer):
    """Respuesta del balance total"""

    total_staked = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_won = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_lost = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    bet_count = serializers.IntegerField()
    won_count = serializers.IntegerField()
    lost_count = serializers.IntegerField()
    void_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()


class BetHistorySummarySerializer(serializers.Serializer):
    """Resumen del historial filtrado"""

    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_staked = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_won = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_lost = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    bet_count = serializers.IntegerField()
    won_count = serializers.IntegerField()
    lost_count = serializers.IntegerField()
    void_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()


class BetHistoryQuerySerializer(serializers.Serializer):
    """Valida los query params del historial"""

    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError("start_date no puede ser mayor que end_date")
        return data


class DailyBalanceQuerySerializer(serializers.Serializer):
    """Valida el query param de fecha para balance diario"""

    date = serializers.DateField()
