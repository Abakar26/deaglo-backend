from rest_framework import serializers
from api_gateway.models import TypeCurrency
from api_gateway.serializers import CurrencySerializer


class CurrencyField(serializers.DictField, CurrencySerializer):
    """
    Reads code and country_name and returns the associated type currency
    """

    def to_representation(self, value):
        return CurrencySerializer(value).data

    def to_internal_value(self, data):
        if not {"code", "country_name"}.issubset(data):
            raise serializers.ValidationError("code and countryName are required")

        try:
            return TypeCurrency.objects.get(
                code=data.get("code"), country_name=data.get("country_name")
            )
        except TypeCurrency.DoesNotExist:
            raise serializers.ValidationError("Currency not found.")
