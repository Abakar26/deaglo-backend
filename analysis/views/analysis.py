# from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response

from analysis.models import Analysis
from analysis.serializers import AnalysisSerializer
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin
from hedge_simulation.models import HedgeSimulation
from hedge_simulation.serializer import HedgeIRRSerializer
from margin_simulation.models import MarginSimulation
from margin_simulation.serializers import MarginSimulationSerializer
from strategy_simulation.models import StrategySimulation
from strategy_simulation.serializers import StrategySimulationSerializer
from ..filters import AnalysisFilter


@method_decorator(swagger_auto_schema(tags=["Analysis"]), "get")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "post")
class AnalysisListCreateAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of analyses created by authenticated user"""

    queryset = Analysis.objects.filter()
    serializer_class = AnalysisSerializer
    filterset_class = AnalysisFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        analysis_order = self.request.query_params.get("order_by")
        queryset = super().get_queryset()
        if analysis_order:
            queryset = queryset.order_by(analysis_order)

        return self.paginate_queryset(self.filter_queryset(queryset))

    def get(self, request, *args, **kwargs):
        instances = self.get_queryset()
        analyses = self.get_serializer(instances, many=True).data
        withSimulations = self.request.query_params.get("with_simulations")
        page = self.request.query_params.get("page")
        analyses_with_simulation = []
        if withSimulations != None and withSimulations.isnumeric():
            take = int(withSimulations)
            for analysis in analyses:
                strategy_instances = StrategySimulation.objects.filter(
                    analysis_id=analysis["analysis_id"]
                ).order_by("-date_updated")[:take]
                margin_instances = MarginSimulation.objects.filter(
                    analysis_id=analysis["analysis_id"]
                ).order_by("-date_updated")[:take]
                hedge_instances = HedgeSimulation.objects.filter(
                    analysis_id=analysis["analysis_id"]
                ).order_by("-date_updated")[:take]
                strategy_simulations = StrategySimulationSerializer(
                    strategy_instances, many=True
                ).data
                margin_simulations = MarginSimulationSerializer(
                    margin_instances, many=True
                ).data
                hedge_simulations = HedgeIRRSerializer(hedge_instances, many=True).data
                simulations = (
                    strategy_simulations + margin_simulations + hedge_simulations
                )
                simulations.sort(
                    key=lambda simulation: str(simulation["date_updated"]), reverse=True
                )
                analyses_with_simulation.append(
                    {**analysis, "simulations": simulations[:take]}
                )
        data = analyses_with_simulation if analyses_with_simulation else analyses
        response = self.get_paginated_response(data)
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(swagger_auto_schema(tags=["Analysis"]), "get")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "put")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "delete")
class AnalysisApiView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for destroying analysis created by authenticated user"""

    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    lookup_field = "analysis_id"
