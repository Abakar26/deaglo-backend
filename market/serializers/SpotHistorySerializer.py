from datetime import date
from dateutil import relativedelta
from rest_framework import serializers

from market.models import SpotHistory
from api_gateway.utils.fields import CurrencyField
from time_series.serializers import SpotHistoryDataSerializer
from time_series.utils import SpotHistoryDataHelper


class SpotHistorySerializer(serializers.ModelSerializer):
    base_currency = CurrencyField()
    foreign_currency = CurrencyField()
    duration_months = serializers.IntegerField(source="duration")
    is_default = serializers.BooleanField(read_only=True)
    spot_history_data = SpotHistoryDataSerializer(read_only=True, many=True)

    class Meta:
        model = SpotHistory
        fields = [
            "name",
            "spot_history_id",
            "base_currency",
            "foreign_currency",
            "duration_months",
            "is_default",
            "layered",
            "spot_history_data",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_to = date.today()
        date_from = date.today() - relativedelta.relativedelta(months=instance.duration)
        representation["spot_history_data"] = SpotHistoryDataHelper(
            base_currency=instance.base_currency.code,
            foreign_currency=instance.foreign_currency.code,
            date_from=date_from,
            date_to=date_to,
        ).serializer_spot_history_date()
        return representation
