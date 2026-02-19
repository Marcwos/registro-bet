from rest_framework import serializers


class SendVerificationRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class VerifyEmailRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    code = serializers.CharField(min_length=6, max_length=6)


class SendPasswordRecoverySerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)


class ChangePasswordRequestSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
