from rest_framework import serializers

from analysis.models import Analysis, TypeCategory
from api_gateway.utils.fields import ForeignKeyCharField, CurrencyField


class AnalysisSerializer(serializers.ModelSerializer):
    date_added = serializers.DateTimeField(read_only=True)
    category = ForeignKeyCharField(
        model=TypeCategory,
        column_name="name",
        source="type_category",
        help_text="Category name",
    )
    base_currency = CurrencyField()
    foreign_currency = CurrencyField()
    organization = serializers.CharField(read_only=True, source="organization.name")

    class Meta:
        model = Analysis
        fields = [
            "analysis_id",
            "date_added",
            "name",
            "category",
            "base_currency",
            "foreign_currency",
            "organization",
        ]
