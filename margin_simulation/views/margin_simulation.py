from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.response import Response

from analysis.models import Analysis
from api_gateway.core.adapter import CoreAdapter
from api_gateway.exceptions import GenericAPIError
from api_gateway.settings.config import AWS
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from margin_simulation.models import MarginSimulation
from margin_simulation.serializers import MarginSimulationSerializer
from strategy_simulation.models import StrategySimulation


@method_decorator(swagger_auto_schema(tags=["Margin Simulation"]), "get")
@method_decorator(swagger_auto_schema(tags=["Margin Simulation"]), "post")
# TODO: Admin might have the option to view all
class MarginSimulationListCreateAPIView(
    NonDeletedQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of margin simulations created by authenticated user"""

    queryset = MarginSimulation.objects.filter()
    serializer_class = MarginSimulationSerializer

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            analysis_id = self.kwargs.get("analysis_id")
            analysis = Analysis.objects.get(
                pk=analysis_id, user=self.request.user, is_deleted=False
            )
            return queryset.filter(analysis=analysis)
        except ObjectDoesNotExist:
            raise GenericAPIError("Object not found", code=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            analysis_id = self.kwargs.get("analysis_id")

            try:
                if analysis_id is None:
                    raise serializers.ValidationError(
                        "Please enter a valid analysis id"
                    )
                analysis = Analysis.objects.get(
                    analysis_id=analysis_id,
                    is_deleted=False,
                    user=self.request.user,
                )

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                strategy_simulation_id = request.data.get("strategy_simulation_id")
                StrategySimulation.objects.get(
                    pk=strategy_simulation_id,
                    is_deleted=False,
                    analysis=analysis,
                )

                instance = serializer.save(analysis=analysis)
                headers = self.get_success_headers(serializer.data)

                core_payload = CoreAdapter.margin_simulation(
                    request.user.user_id, instance.result_id, serializer.data
                )

                simulation_sent = AWS.sqs.enqueue(
                    core_payload, message_group_id=core_payload["data"]["strategy_id"]
                )

                if not simulation_sent:
                    raise GenericAPIError("Failed to enqueue simulation", code=500)

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )
            except ObjectDoesNotExist:
                raise GenericAPIError(
                    "Analysis not found", code=status.HTTP_404_NOT_FOUND
                )


@method_decorator(swagger_auto_schema(tags=["Margin Simulation"]), "get")
@method_decorator(swagger_auto_schema(tags=["Margin Simulation"]), "put")
@method_decorator(swagger_auto_schema(tags=["Margin Simulation"]), "delete")
@method_decorator(swagger_auto_schema(auto_schema=None), "patch")
class MarginSimulationRetrieveUpdateDestroyAPIView(
    NonDeletedQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for retrieving margin simulation created by authenticated user"""

    queryset = MarginSimulation.objects.all()
    serializer_class = MarginSimulationSerializer
    lookup_field = "margin_simulation_id"

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            analysis_id = self.kwargs.get("analysis_id")
            analysis = Analysis.objects.get(
                pk=analysis_id, user=self.request.user, is_deleted=False
            )
            return queryset.filter(analysis=analysis)
        except ObjectDoesNotExist:
            raise GenericAPIError("Object not found", code=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        simulation = super().update(request, *args, **kwargs)
        core_payload = CoreAdapter.margin_simulation(
            request.user.user_id,
            simulation.data["result_id"],
            {
                **simulation.data,
                "margin_simulation_id": kwargs.get("margin_simulation_id"),
            },
        )
        simulation_sent = AWS.sqs.enqueue(
            core_payload, message_group_id=core_payload["data"]["strategy_id"]
        )
        if not simulation_sent:
            raise GenericAPIError("Failed to enqueue simulation", code=500)
        return simulation

    def perform_update(self, serializer):
        with transaction.atomic():
            try:
                requested_strategy_simulation = serializer.validated_data.get(
                    "strategy_simulation"
                )
                instance = self.get_object()
                instance.analysis.strategy_simulation.get(
                    pk=requested_strategy_simulation.strategy_simulation_id,
                    is_deleted=False,
                )
                return super().perform_update(serializer)

            except (ObjectDoesNotExist, Http404):
                raise GenericAPIError(
                    "Object not found", code=status.HTTP_404_NOT_FOUND
                )

    def patch(self, request, *args, **kwargs):
        return Response(
            {"error": "Partial update (PATCH) not implemented."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def perform_destroy(self, instance):
        instance.delete()
