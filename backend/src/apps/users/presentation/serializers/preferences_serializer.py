from rest_framework import serializers


class UpdatePreferencesSerializer(serializers.Serializer):
    theme_preference = serializers.ChoiceField(
        choices=["light", "dark"],
        required=False,
    )
    timezone = serializers.CharField(max_length=50, required=False)

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("Debes enviar al menos un campo para actualizar.")
        return data


class PreferencesResponseSerializer(serializers.Serializer):
    theme_preference = serializers.CharField()
    timezone = serializers.CharField()
