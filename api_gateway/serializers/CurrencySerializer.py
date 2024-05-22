from rest_framework import serializers

from api_gateway.models import TypeCurrency


class CurrencySerializer(serializers.ModelSerializer):
    code = serializers.CharField(min_length=3, max_length=3)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = TypeCurrency
        fields = [
            "code",
            "name",
            "country_name",
        ]
