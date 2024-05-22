from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from analysis.models import Analysis, SimulationEnviroment
from analysis.serializers import SimulationEnvironmentSerializer
from api_gateway.core.adapter import CoreAdapter
from api_gateway.exceptions import GenericAPIError
from api_gateway.serializers import CurrencySerializer
from api_gateway.settings import AWS
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from strategy_simulation.models import (
    StrategyInstance,
    StrategySimulation,
    Strategy,
)
from strategy_simulation.serializers import (
    StrategyInstanceSerializer,
    StrategySimulationSerializer,
)


@method_decorator(swagger_auto_schema(tags=["Strategy Simulation"]), "get")
@method_decorator(swagger_auto_schema(tags=["Strategy Simulation"]), "post")
# This would need to be further filtered by user
class StrategySimulationListAPIView(
    NonDeletedQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of strategy simulations created by the authenticated user"""

    queryset = StrategySimulation.objects.all()
    serializer_class = StrategySimulationSerializer

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
            helper = StrategySimulationViewHelper(user=self.request.user)
            analysis_id = self.kwargs.get("analysis_id")
            try:
                # Get associated Analysis
                if analysis_id is None:
                    raise serializers.ValidationError(
                        "Please enter a valid analysis id"
                    )
                analysis = Analysis.objects.get(
                    pk=analysis_id, user=self.request.user, is_deleted=False
                )

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                strategy_simulation_data = serializer.validated_data
                strategy_simulation_data.pop("strategy_instance", None)
                strategy_simulation_data.pop("hidden_strategy_leg", None)

                environment = strategy_simulation_data.pop("simulation_environment")
                simulation_environment = SimulationEnvironmentSerializer(
                    data=environment
                )
                simulation_environment.is_valid(raise_exception=True)
                strategy_simulation_data[
                    "simulation_environment"
                ] = simulation_environment.save()

                # TODO: fix the validation before we start saving things, we should only save after EVERYTHING is validated
                # Create Strategy Simulation with associated Analysis
                strategy_simulation = StrategySimulation.objects.create(
                    analysis=analysis,
                    **strategy_simulation_data,
                )

                helper.map_strategy_instance(request, strategy_simulation)

                response_serializer = self.get_serializer(strategy_simulation)
                headers = self.get_success_headers(response_serializer.data)

                core_payload = CoreAdapter.strategy_simulation(
                    request.user.user_id,
                    strategy_simulation.result_id,
                    {
                        **response_serializer.data,
                        "base_currency": CurrencySerializer(
                            analysis.base_currency
                        ).data,
                        "foreign_currency": CurrencySerializer(
                            analysis.foreign_currency
                        ).data,
                    },
                )

                simulation_sent = AWS.sqs.enqueue(
                    core_payload, message_group_id=core_payload["simulation_id"]
                )
                if not simulation_sent:
                    raise GenericAPIError("Failed to enqueue simulation", code=500)

                # Clean up hidden strategy leg from response
                for index, strategy in enumerate(
                    response_serializer.data["strategy_instance"]
                ):
                    for index, leg in enumerate(strategy["legs"]):
                        leg.pop("hidden_strategy_leg", None)

                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )

            except ObjectDoesNotExist:
                raise GenericAPIError(
                    "Object not found", code=status.HTTP_404_NOT_FOUND
                )


@method_decorator(swagger_auto_schema(tags=["Strategy Simulation"]), "get")
@method_decorator(swagger_auto_schema(tags=["Strategy Simulation"]), "put")
@method_decorator(swagger_auto_schema(tags=["Strategy Simulation"]), "delete")
@method_decorator(swagger_auto_schema(auto_schema=None), "patch")
class StrategySimulationRetrieveUpdateDestroyAPIView(
    NonDeletedQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for retrieving strategy simulation created by authenticated user"""

    queryset = StrategySimulation.objects.all()
    serializer_class = StrategySimulationSerializer
    lookup_field = "strategy_simulation_id"

    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            analysis_id = self.kwargs.get("analysis_id")
            analysis = Analysis.objects.get(
                pk=analysis_id, user=self.request.user, is_deleted=False
            )
            return queryset.filter(analysis=analysis)
        except ObjectDoesNotExist:
            raise NotFound(
                code=status.HTTP_404_NOT_FOUND,
                detail={"status": "Not Found", "message": "Analysis not found"},
            )

    def patch(self, request, *args, **kwargs):
        return Response(
            {"error": "Partial update (PATCH) not implemented."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            helper = StrategySimulationViewHelper(user=self.request.user)
            try:
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)

                environment = serializer.validated_data.pop(
                    "simulation_environment", None
                )
                if environment:
                    simulation_environment = SimulationEnvironmentSerializer(
                        data=environment
                    )
                    simulation_environment.is_valid(raise_exception=True)
                    for key, value in simulation_environment.validated_data.items():
                        setattr(instance.simulation_environment, key, value)
                    instance.simulation_environment.save()

                serializer.validated_data.pop("strategy_instance", None)
                serializer.save()
                analysis_id = self.kwargs.get("analysis_id")
                analysis = Analysis.objects.get(
                    pk=analysis_id, user=self.request.user, is_deleted=False
                )

                # TODO: We really need to valdiate the new leg instances before we start deleting the old ones
                old_instances = instance.strategy_instance.all().delete()

                helper.map_strategy_instance(request, instance)
                core_payload = CoreAdapter.strategy_simulation(
                    request.user.user_id,
                    instance.result_id,
                    {
                        **serializer.data,
                        "base_currency": CurrencySerializer(
                            analysis.base_currency
                        ).data,
                        "foreign_currency": CurrencySerializer(
                            analysis.foreign_currency
                        ).data,
                    },
                )

                simulation_sent = AWS.sqs.enqueue(
                    core_payload, message_group_id=core_payload["simulation_id"]
                )
                if not simulation_sent:
                    raise GenericAPIError("Failed to enqueue simulation", code=500)

                # Clean up hidden strategy leg from response
                for index, strategy in enumerate(serializer.data["strategy_instance"]):
                    for index, leg in enumerate(strategy["legs"]):
                        leg.pop("hidden_strategy_leg", None)

                return Response(serializer.data)

            except (ObjectDoesNotExist, Http404):
                # TODO: More robust error handling
                raise GenericAPIError(
                    "Object not found", code=status.HTTP_404_NOT_FOUND
                )

    def perform_destroy(self, instance):
        instance.delete()


class StrategySimulationViewHelper:
    def __init__(self, user):
        self.user = user

    def map_strategy_instance(self, request, strategy_simulation):
        # Create the Strategy Instances
        strategy_instances_data = request.data.get("strategy_instance", [])

        for index, instance_data in enumerate(strategy_instances_data):
            # Get required strategy data
            strategy_id = instance_data.get("strategy_id")
            strategy_leg_list = instance_data.get("legs", [])

            # Iterate the strategy leg instances
            for leg_data in strategy_leg_list:
                # leg_id = leg_data.pop("strategy_leg_id")
                leg_instance_serializer = StrategyInstanceSerializer(data=leg_data)
                leg_instance_serializer.is_valid(raise_exception=True)
                leg_instance_serializer.validated_data.pop("hidden_strategy_leg")
                leg_id = leg_instance_serializer.validated_data.pop(
                    "strategy_leg_id", None
                )

                # TODO: fix the validation before we start saving things
                # TODO: In the future, custom strategy will be shared with other users,
                #       Would need to check permissions another way
                # TODO! - can we use bulk create here?
                # Create the leg instance accordingly
                strategy = Strategy.objects.get(
                    Q(**{"created_by_user": self.user})
                    | Q(**{"created_by_user__isnull": True}),
                    strategy_id=strategy_id,
                    is_deleted=False,
                )
                strategy_leg = strategy.strategy_leg.get(
                    strategy_leg_id=leg_id, is_deleted=False
                )
                StrategyInstance.objects.create(
                    strategy_simulation=strategy_simulation,
                    strategy_leg=strategy_leg,
                    instance_group=index + 1,
                    **leg_instance_serializer.validated_data,
                )
