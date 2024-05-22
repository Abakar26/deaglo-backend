from datetime import date
from dateutil import relativedelta
from rest_framework import serializers

from analysis.serializers import SimulationEnvironmentSerializer
from api_gateway.models import TypeStatus
from api_gateway.utils.fields import ForeignKeyCharField
from api_gateway.serializers import CurrencySerializer
from strategy_simulation.models import StrategySimulation
from strategy_simulation.serializers import (
    StrategyInstanceSerializer,
    StrategyInstanceMasterSerializer,
)
from time_series.serializers import SpotHistoryDataSerializer
from time_series.utils import SpotHistoryDataHelper


class StrategySimulationSerializer(serializers.ModelSerializer):
    # analysis = AnalysisSerializer(read_only=True)
    id = serializers.CharField(source="strategy_simulation_id", read_only=True)
    type = serializers.ReadOnlyField(default="STRATEGY")
    status = ForeignKeyCharField(
        model=TypeStatus,
        column_name="name",
        source="type_status",
        help_text="Status name",
    )
    strategy_instance = serializers.ListSerializer(
        child=StrategyInstanceMasterSerializer()
    )
    simulation_environment = SimulationEnvironmentSerializer(required=True)
    spot_history_data = SpotHistoryDataSerializer(read_only=True, many=True)
    simulation_status = serializers.CharField(read_only=True)

    class Meta:
        model = StrategySimulation
        fields = [
            "id",
            "name",
            "type",
            "strategy_simulation_id",
            "result_id",
            "date_added",
            "date_updated",
            "simulation_environment",
            "status",
            "start_date",
            "end_date",
            "is_base_sold",
            "notional",
            "initial_spot_rate",
            "initial_forward_rate",
            "spread",
            "strategy_instance",
            "pin",
            "spot_history_data",
            "simulation_status",
        ]

    def to_representation(self, instance):
        data = {}
        data["strategy_simulation_id"] = instance.pk
        data["id"] = instance.pk
        data["result_id"] = instance.result_id
        data["name"] = instance.name
        data["type"] = "STRATEGY"
        data["date_added"] = instance.date_added
        data["date_updated"] = instance.date_updated
        data["simulation_environment"] = SimulationEnvironmentSerializer(
            instance.simulation_environment
        ).data
        data["status"] = instance.type_status.name
        data["start_date"] = instance.start_date
        data["end_date"] = instance.end_date
        data["is_base_sold"] = instance.is_base_sold
        data["notional"] = instance.notional
        data["initial_spot_rate"] = instance.initial_spot_rate
        data["initial_forward_rate"] = instance.initial_forward_rate
        data["strategy_instance"] = self.get_strategy_instance(instance)
        data["pin"] = instance.pin
        data["simulation_status"] = instance.simulation_status

        if instance.start_date <= date.today():
            date_to = instance.start_date
            date_from = instance.start_date - relativedelta.relativedelta(months=12)
            base_currency = (
                instance.analysis.foreign_currency.code
                if instance.is_base_sold
                else instance.analysis.base_currency.code
            )
            foreign_currency = (
                instance.analysis.base_currency.code
                if instance.is_base_sold
                else instance.analysis.foreign_currency.code
            )
            data["spot_history_data"] = SpotHistoryDataHelper(
                base_currency=base_currency,
                foreign_currency=foreign_currency,
                date_from=date_from,
                date_to=date_to,
            ).serializer_spot_history_date()

        return data

    def get_strategy_instance(self, obj):
        group = {}
        global_name_counter = {}

        # Iterate through all the strategy instances
        for instance in obj.strategy_instance.all():
            if instance.strategy_leg:
                strategy = instance.strategy_leg.strategy
                is_custom = True if strategy.created_by_user is not None else False

                # Group the strategy and leg with overrides
                if instance.instance_group not in group.keys():
                    base_name = strategy.name
                    if base_name in global_name_counter:
                        global_name_counter[base_name] += 1
                    else:
                        global_name_counter[base_name] = 1
                    # Generate a unique name with the counter
                    unique_name = f"{base_name}-{global_name_counter[base_name]}"
                    group[instance.instance_group] = {
                        "strategy_id": strategy.pk,
                        "is_custom": is_custom,
                        "name": unique_name,
                        "description": strategy.description,
                        "legs": [],
                    }
                group[instance.instance_group]["legs"].append(
                    StrategyInstanceSerializer(instance).data
                )

        return list(group.values())
