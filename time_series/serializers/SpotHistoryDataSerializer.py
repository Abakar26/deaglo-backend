from rest_framework import serializers

from api_gateway.utils.fields import CurrencyField
from time_series.utils.serialize_spot_history_data import SpotHistoryDataHelper


class SpotHistoryDataSerializer(serializers.Serializer):
    class Meta:
        fields = [
            "date",
            "rate",
        ]

    def to_representation(self, instance):
        data = dict()
        data["date"] = instance["date"]
        data["rate"] = instance["rate"]
        return data


class SpotHistoryDataRequestSerializer(serializers.Serializer):
    base_currency = CurrencyField()
    foreign_currency = CurrencyField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_base_sold = serializers.BooleanField()
    spot_history_data = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "base_currency",
            "foreign_currency",
            "start_date",
            "end_date",
            "is_base_sold",
            "spot_history_data",
        ]

    def get_spot_history_data(self, obj):
        base_currency = (
            obj["foreign_currency"].code
            if obj["is_base_sold"]
            else obj["base_currency"].code
        )
        foreign_currency = (
            obj["base_currency"].code
            if obj["is_base_sold"]
            else obj["foreign_currency"].code
        )
        return SpotHistoryDataHelper(
            base_currency=base_currency,
            foreign_currency=foreign_currency,
            date_from=obj["start_date"],
            date_to=obj["end_date"],
        ).serializer_spot_history_date()
