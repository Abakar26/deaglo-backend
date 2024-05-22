from rest_framework import serializers
from django.contrib.auth.password_validation import (
    validate_password as default_validate_password,
)
from django.core.exceptions import ValidationError

from api_gateway.utils.fields import ForeignKeyCharField
from authentication.models import User, TypeUserRole
from authentication.utils import send_otp_via_email, user_init
from organization.models import Organization


class UserAdminSerializer(serializers.ModelSerializer):
    user_role = ForeignKeyCharField(
        model=TypeUserRole,
        column_name="name",
        source="type_user_role",
        help_text="User role by name",
    )
    organization = ForeignKeyCharField(
        model=Organization, column_name="name", help_text="Organization by name"
    )
    sso = serializers.UUIDField(
        source="sso.linkedin_id", help_text="Linkedin Id", required=False
    )
    last_login = serializers.DateTimeField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "date_added",
            "date_updated",
            "last_login",
            "is_deleted",
            "is_active",
            "is_verified",
            "user_role",
            "first_name",
            "last_name",
            "email",
            "user_role",
            "organization",
            "city",
            "country",
            "sso",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super(UserAdminSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.method == "POST":
            self.fields["password"].required = True
        else:
            self.fields["password"].required = False

    def validate_password(self, value):
        default_validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user_init(user)
        send_otp_via_email(user)
        return user

    def update(self, instance, validated_data):
        validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
