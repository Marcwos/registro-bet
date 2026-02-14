from rest_framework import serializers

class RegisterRequestSerializer(serializers.Serializer):
    """Valida los datos de entrada para el registro"""
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only= True)

class RegisterResponseSerializer(serializers.Serializer):
    """Fomatea la respuesta de registro"""
    id = serializers.UUIDField()
    email = serializers.EmailField()
    role = serializers.CharField()
    is_email_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField()