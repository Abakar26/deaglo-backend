from datetime import date
from dateutil import relativedelta
from rest_framework import serializers

from market.models import FxMovement
from market.serializers.FxCurrencyPairSerializer import FxCurrencyPairSerializer


class FxMovementSerializer(serializers.ModelSerializer):
    currency_pairs = FxCurrencyPairSerializer(many=True)
    duration_months = serializers.IntegerField(source="duration")
    is_default = serializers.BooleanField(read_only=True)

    class Meta:
        model = FxMovement
        fields = [
            "name",
            "fx_movement_id",
            "currency_pairs",
            "duration_months",
            "is_default",
        ]

    def to_representation(self, instance):
        self.context["duration"] = instance.duration
        return super().to_representation(instance)

    def create(self, validated_data):
        """
        Override of the create method which primary purpose is to create the many-to-many relationship of foreign_currency
        """
        currency_pair_list = validated_data.pop("currency_pairs", [])
        fx_movement = FxMovement.objects.create(**validated_data)
        fx_movement.currency_pairs.set(currency_pair_list)
        return fx_movement

    def update(self, instance, validated_data):
        """
        Override of the update method which primary purpose is to update the many-to-many relationship of foreign_currency
        """
        currency_pairs_list = validated_data.pop("currency_pairs", None)
        if currency_pairs_list is not None:
            instance.currency_pairs.clear()
            instance.currency_pairs.set(currency_pairs_list)

        return super().update(instance, validated_data)
