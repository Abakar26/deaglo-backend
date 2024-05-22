from rest_framework import serializers
from rest_framework.exceptions import NotFound

from analysis.models import Analysis
from analysis.serializers import SimulationEnvironmentSerializer
from api_gateway.models import TypeStatus
from api_gateway.utils.fields import ForeignKeyCharField
from .models import HedgeSimulation
from dateutil.parser import parse


class HedgeIRRSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="hedge_irr_simulation_id", read_only=True)
    type = serializers.ReadOnlyField(default="HEDGE")

    status = ForeignKeyCharField(
        model=TypeStatus,
        column_name="name",
        source="type_status",
        help_text="Status name",
        read_only=True,
    )
    harvest = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(), allow_empty=False),
        allow_empty=False,
        read_only=True,
    )
    simulation_environment = SimulationEnvironmentSerializer()

    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    simulation_status = serializers.CharField(read_only=True)

    def validate(self, attrs: dict):
        """
        Custom validation for the serializer.

        Args:
            attrs (dict): Dictionary of attributes.

        Raises:
            serializers.ValidationError: Raised for validation errors.
            NotFound: Raised if the associated Analysis does not exist.

        Returns:
            dict: Validated attributes.
        """
        request = self.context["request"]

        if request.method in ["POST", "PUT"]:
            harvest = self.initial_data.get("harvest", [])
            if len(harvest) < 2 or not (
                any(entry[1] < 0 for entry in harvest)
                and any(entry[1] > 0 for entry in harvest)
            ):
                raise serializers.ValidationError(
                    "Harvest data must contain at least 1 deployment and 1 harvest"
                )
            period = parse(harvest[-1][0]) - parse(harvest[0][0])
            if period.days < 30:
                raise serializers.ValidationError(
                    "Harvest data must span at least 30 days"
                )
            attrs["start_date"] = harvest[0][0]
            attrs["end_date"] = harvest[-1][0]

        analysis = Analysis.objects.get(
            pk=request.parser_context["kwargs"]["analysis_id"]
        )
        if not analysis or analysis.is_deleted:
            raise NotFound("Analysis does not exist")
        attrs["analysis_id"] = analysis.pk
        return super().validate(attrs)

    def create(self, validated_data: dict):
        """
        Create a new HedgeSimulation instance.

        Args:
            validated_data (dict): Validated data.

        Returns:
            HedgeSimulation: Created instance.
        """
        environment = validated_data.pop("simulation_environment")
        simulation_environment = SimulationEnvironmentSerializer(data=environment)
        simulation_environment.is_valid(raise_exception=True)
        validated_data["simulation_environment"] = simulation_environment.save()
        return super().create(validated_data)

    def update(self, instance: HedgeSimulation, validated_data: dict):
        """
        Update an existing HedgeSimulation instance.

        Args:
            instance (HedgeSimulation): Existing instance.
            validated_data (dict): Validated data.

        Returns:
            HedgeSimulation: Updated instance.
        """
        environment = validated_data.pop("simulation_environment", False)
        if environment:
            simulation_environment = SimulationEnvironmentSerializer(
                instance.simulation_environment, data=environment
            )
            simulation_environment.is_valid(raise_exception=True)
            validated_data["simulation_environment"] = simulation_environment.save()
        return super().update(instance, validated_data)

    class Meta:
        model = HedgeSimulation
        fields = (
            "id",
            "analysis_id",
            "result_id",
            "name",
            "simulation_environment",
            "status",
            "type",
            "harvest",
            "hedge_irr_simulation_id",
            "date_added",
            "date_updated",
            "fwd_rates",
            "start_date",
            "end_date",
            "pin",
            "simulation_status",
        )
