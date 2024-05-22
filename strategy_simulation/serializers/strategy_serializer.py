from rest_framework import serializers

# from rest_framework.utils import model_meta
from django.db import transaction

from strategy_simulation.models import Strategy, StrategyLeg
from .strategy_leg_serializer import StrategyLegSerializer


class StrategySerializer(serializers.ModelSerializer):
    legs = StrategyLegSerializer(source="strategy_leg", many=True, min_length=1)
    is_custom = serializers.SerializerMethodField()

    def get_is_custom(self, obj) -> bool:
        return False if obj.created_by_user is None else True

    class Meta:
        model = Strategy
        fields = [
            "strategy_id",
            "date_added",
            "is_custom",
            "name",
            "description",
            "legs",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            validated_data["created_by_user"] = self.context.get("user", None)
            strategy_leg = validated_data.pop("strategy_leg", None)
            instance = Strategy.objects.create(**validated_data)
            for leg in strategy_leg:
                StrategyLeg.objects.create(strategy=instance, **leg)
            return instance

    def update(self, instance, validated_data):
        # super().update()
        with transaction.atomic():
            # Soft Delete Old Legs
            for object in instance.strategy_leg.all():
                object.delete()

            # Create New Legs
            for leg in validated_data.pop("strategy_leg", None):
                StrategyLeg.objects.create(strategy=instance, **leg)

            # Update other attributes
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Remove any legs that were filtered out (set to None)
        data["legs"] = [leg for leg in data["legs"] if leg is not None]
        return data
