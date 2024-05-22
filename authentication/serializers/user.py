from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from authentication.models import User, UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer responsible for data serialization and validation of user preferences.
    """

    class Meta:
        model = UserPreferences
        exclude = ["id"]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for the User model, handling user data serialization and validation.
    """

    is_verified = serializers.BooleanField(read_only=True)
    sso = serializers.UUIDField(read_only=True, source="sso.linkedin_id")
    preferences = UserPreferencesSerializer(required=False)

    class Meta:
        model = User
        exclude = [
            "user_id",
            "last_login",
            "is_active",
            "date_added",
            "date_updated",
            "is_deleted",
            "type_user_role",
        ]
        depth = 1
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        preferences_data = validated_data.pop("preferences", None)
        if preferences_data is not None:
            preferences_instance = instance.preferences
            for attr, value in preferences_data.items():
                setattr(preferences_instance, attr, value)
            preferences_instance.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
