from rest_framework import serializers

from .user_admin_serializer import UserAdminSerializer
from organization.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    users = UserAdminSerializer(
        many=True,
        read_only=True,
        source="user",
        help_text="List of users that belong to this organization",
    )
    is_deleted = serializers.BooleanField(
        required=False,
        help_text="Admin should have ability to create Organization without it being active",
    )

    class Meta:
        model = Organization
        fields = [
            "organization_id",
            "date_added",
            "date_updated",
            "is_deleted",
            "name",
            "users",
        ]
