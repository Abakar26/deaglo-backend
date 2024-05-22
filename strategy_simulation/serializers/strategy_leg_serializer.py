from rest_framework import serializers

from strategy_simulation.models import StrategyLeg


class StrategyLegSerializer(serializers.ModelSerializer):
    is_call = serializers.BooleanField(allow_null=True)

    class Meta:
        model = StrategyLeg
        fields = [
            "strategy_leg_id",
            "is_call",
            "is_bought",
            "premium",
            "leverage",
            "strike",
            "barrier_type",
            "barrier_level",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        strategy_leg__is_deleted = self.context.get("strategy_leg__is_deleted", None)
        if (
            strategy_leg__is_deleted is not None
            and instance.is_deleted != strategy_leg__is_deleted
        ):
            return (
                None  # Skip this leg if the context includes is_deleted filter for legs
            )
        return data
