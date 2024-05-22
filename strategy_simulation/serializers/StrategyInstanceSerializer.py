from rest_framework import serializers

from strategy_simulation.models import StrategyInstance
from .strategy_leg_serializer import StrategyLegSerializer


class StrategyInstanceSerializer(serializers.ModelSerializer):
    strategy_leg_id = serializers.UUIDField(
        required=True, help_text="Default or custom strategy leg id"
    )
    hidden_strategy_leg = serializers.HiddenField(default=None)

    class Meta:
        model = StrategyInstance
        fields = [
            "strategy_leg_id",
            "date_added",
            "premium_override",
            "leverage_override",
            "strike_override",
            "hidden_strategy_leg",
        ]

    def to_representation(self, instance):
        data = {}
        data["strategy_leg_id"] = instance.strategy_leg.pk
        data["date_added"] = instance.date_added
        data["premium_override"] = instance.premium_override
        data["leverage_override"] = instance.leverage_override
        data["strike_override"] = instance.strike_override
        data["hidden_strategy_leg"] = StrategyLegSerializer(instance.strategy_leg).data
        return data


class StrategyInstanceMasterSerializer(serializers.Serializer):
    strategy_id = serializers.UUIDField(help_text="Default or custom strategy id")
    is_custom = serializers.BooleanField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    legs = StrategyInstanceSerializer(many=True)

    class Meta:
        fields = [
            "strategy_id",
            "is_custom",
            "name",
            "description",
            "legs",
        ]
