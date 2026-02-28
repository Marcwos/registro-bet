from rest_framework import serializers


class AdminStatsResponseSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_bets = serializers.IntegerField()
    total_audit_events = serializers.IntegerField()
