from datetime import date
from dateutil import relativedelta
from rest_framework import serializers
from api_gateway.models import TypeCurrency
from market.models import FxCurrencyPair
from api_gateway.utils.fields import CurrencyField
from time_series.serializers import SpotHistoryDataSerializer
from time_series.utils import SpotHistoryDataHelper


class FxCurrencyPairSerializer(serializers.ModelSerializer):
    base_currency = CurrencyField()
    foreign_currency = CurrencyField()
    spot_history_data = SpotHistoryDataSerializer(read_only=True, many=True)

    def to_internal_value(self, data):
        if not {"base_currency", "foreign_currency"}.issubset(data):
            raise serializers.ValidationError(
                "base_currency and foreign_currency are required"
            )
        try:
            base_currency = CurrencyField().to_internal_value(data.get("base_currency"))
            foreign_currency = CurrencyField().to_internal_value(
                data.get("foreign_currency")
            )
            instance, _ = FxCurrencyPair.objects.get_or_create(
                base_currency=base_currency, foreign_currency=foreign_currency
            )
            return instance
        except TypeCurrency.DoesNotExist:
            raise serializers.ValidationError("Currency not found.")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        date_to = date.today()
        date_from = date.today() - relativedelta.relativedelta(
            months=self.context["duration"]
        )
        representation["spot_history_data"] = SpotHistoryDataHelper(
            base_currency=instance.base_currency.code,
            foreign_currency=instance.foreign_currency.code,
            date_from=date_from,
            date_to=date_to,
        ).serializer_spot_history_date()
        return representation

    class Meta:
        model = FxCurrencyPair
        fields = [
            "base_currency",
            "foreign_currency",
            "spot_history_data",
        ]
