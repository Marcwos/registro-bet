from rest_framework import serializers


class AuditLogResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    action = serializers.CharField()
    entity_type = serializers.CharField()
    entity_id = serializers.UUIDField(allow_null=True)
    metadata = serializers.DictField()
    ip_address = serializers.CharField()
    created_at = serializers.DateTimeField()


class AuditLogListResponseSerializer(serializers.Serializer):
    items = AuditLogResponseSerializer(many=True)
    total = serializers.IntegerField()
