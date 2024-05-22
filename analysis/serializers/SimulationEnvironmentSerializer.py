from rest_framework import serializers

from analysis.models import SimulationEnviroment


class SimulationEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationEnviroment
        fields = [
            "date_added",
            "name",
            "volatility",
            "skew",
            "appreciation_percent",
        ]
