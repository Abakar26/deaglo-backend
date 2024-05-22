from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from analysis.models import Workspace
from api_gateway.utils.fields import CurrencyField
from analysis.serializers import AnalysisSerializer


class WorkspaceSerializer(ModelSerializer):
    """
    Serializer for Workspace model.
    This serializer includes fields for serializing Workspace objects.
    """

    analysis = AnalysisSerializer(many=True, read_only=True)
    base_currency = CurrencyField(required=False, allow_null=True)

    class Meta:
        model = Workspace
        fields = (
            "workspace_id",
            "base_currency",
            "name",
            "date_added",
            "date_updated",
            "is_deleted",
            "analysis",
        )
        extra_kwargs = {"description": {"allow_blank": True, "required": False}}
