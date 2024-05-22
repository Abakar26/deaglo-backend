from rest_framework import serializers

# from authentication.serializers import UserSerializer

from analysis.serializers import AnalysisSerializer
from strategy_simulation.models import StrategySimulation
from margin_simulation.models import MarginSimulation
from api_gateway.models import TypeStatus
from api_gateway.utils.fields import ForeignKeyCharField, ForeignKeyUUIDField


class MarginStrategySimulationSerializer(serializers.ModelSerializer):
    status = ForeignKeyCharField(
        model=TypeStatus,
        column_name="name",
        source="type_status",
        help_text="Status name",
    )

    class Meta:
        model = StrategySimulation
        fields = ["name", "status", "date_updated"]


class MarginSimulationSerializer(serializers.ModelSerializer):
    # analysis = AnalysisSerializer(read_only=True)
    id = serializers.CharField(source="margin_simulation_id", read_only=True)
    type = serializers.ReadOnlyField(default="MARGIN")

    status = ForeignKeyCharField(
        model=TypeStatus,
        column_name="name",
        source="type_status",
        help_text="Status name",
    )
    strategy_simulation_id = ForeignKeyUUIDField(
        model=StrategySimulation,
        column_name="strategy_simulation_id",
        source="strategy_simulation",
    )

    strategy_result_id = ForeignKeyUUIDField(
        model=StrategySimulation,
        column_name="result_id",
        source="strategy_simulation",
        read_only=True,
    )

    is_strategy_simulation_deleted = serializers.BooleanField(
        source="strategy_simulation.is_deleted",
        read_only=True,
    )

    start_date = serializers.DateField(
        source="strategy_simulation.start_date", read_only=True
    )
    end_date = serializers.DateField(
        source="strategy_simulation.end_date", read_only=True
    )

    strategy_simulation = MarginStrategySimulationSerializer(read_only=True)
    simulation_status = serializers.CharField(read_only=True)

    class Meta:
        model = MarginSimulation
        fields = [
            "id",
            "name",
            "margin_simulation_id",
            "result_id",
            "strategy_result_id",
            "date_added",
            "date_updated",
            "type",
            # "analysis",
            "start_date",
            "end_date",
            "status",
            "strategy_simulation_id",
            "strategy_simulation",
            "is_strategy_simulation_deleted",
            "minimum_transfer_amount",
            "initial_margin_percentage",
            "variation_margin_percentage",
            "pin",
            "simulation_status",
        ]
