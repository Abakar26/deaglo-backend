from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models import Analysis
from analysis.utils import SimulationListHelper
from django.shortcuts import get_object_or_404


class ListSimulationView(APIView):
    def get(self, request, analysis_id):
        analysis = get_object_or_404(Analysis, analysis_id=analysis_id)
        simulation_order = self.request.query_params.get("order_by") or "date_added"
        simulation_type = self.request.query_params.get("type")
        simulation_status = self.request.query_params.get("status")
        response = SimulationListHelper.to_representation(
            analysis, request, simulation_order, simulation_type, simulation_status
        )
        return response


class TogglePinnedSimulationView(APIView):
    # TODO migration this code in patch function for each simulation when patch is implemented
    def patch(self, request, simulation_type, simulation_id):
        SimulationListHelper.toggle_simulation(simulation_type, simulation_id)
        return Response({"status": "success"})
