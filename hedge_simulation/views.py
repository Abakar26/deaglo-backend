import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.urls import reverse
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.test import APIClient

from api_gateway.core.adapter import CoreAdapter
from api_gateway.exceptions import GenericAPIError
from api_gateway.settings import AWS
from .models import HedgeSimulation
from .serializer import HedgeIRRSerializer
from uuid import uuid4

logger = logging.getLogger()


def send_hedge_to_core(request: Request, serializer: HedgeIRRSerializer, **kwargs):
    """
    Save a HedgeSimulation instance, authenticate the user, and send data to the core.

    Args:
        request (Request): The HTTP request object.
        serializer (HedgeIRRSerializer): Serializer instance for the HedgeSimulation data.
        **kwargs: Additional keyword arguments.

    Raises:
        GenericAPIError: Raised if there's an issue with enqueuing the simulation.

    Details:
        - Saves the HedgeSimulation instance.
        - Authenticates the user for the core API.
        - Sends a POST request to the core API with simulation details.
        - Constructs a payload for the CoreAdapter.
        - Enqueues the payload to AWS SQS with the simulation ID as the message group ID.

    """
    with transaction.atomic():
        client = APIClient()
        instance = serializer.save()

        if request.method == "PATCH" and request.data.keys() not in [
            "harvest",
            "simulation_environment",
            "fwd_rates",
        ]:
            return True
        client.force_authenticate(user=request.user)
        response = client.post(
            reverse("spot-rate"),
            {
                "base_currency": instance.analysis.base_currency.code,
                "foreign_currency": instance.analysis.foreign_currency.code,
            },
            format="json",
        )
        logger.info(f"Spot Rate: {response.data}")
        spot_rate = response.data.get("spot_rate", 1)
        payload = CoreAdapter.hedge_simulation(
            request.user.user_id,
            instance.result_id,
            {
                "simulation_id": str(instance.pk),
                "skew": instance.simulation_environment.skew,
                "volatility": instance.simulation_environment.volatility,
                "spot_rate": float(spot_rate),
                "base_currency": {
                    "symbol": instance.analysis.base_currency.code,
                    "name": instance.analysis.base_currency.name,
                },
                "foreign_currency": {
                    "symbol": instance.analysis.foreign_currency.code,
                    "name": instance.analysis.foreign_currency.name,
                },
                "fwd_rates": instance.fwd_rates,
                "harvest": request.data["harvest"],
            },
        )
        simulation_sent = AWS.sqs.enqueue(payload, message_group_id=str(instance.pk))
        if not simulation_sent:
            raise GenericAPIError("Failed to enqueue simulation", code=500)


@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "post")
@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "get")
class HedgeIRRListCreateView(ListCreateAPIView):
    """
    List and create HedgeSimulation instances for a specific analysis.

    Attributes:
        serializer_class (class): Serializer for data conversion.
        queryset (QuerySet): Base query set of all HedgeSimulation instances.

    Methods:
        get_queryset(): Retrieve filtered queryset based on analysis and user.
        perform_create(serializer): Create a new HedgeSimulation and send to the core.

    Usage:
        Used in a RESTFul API for listing and creating HedgeSimulation instances tied to a specific analysis.
    """

    serializer_class = HedgeIRRSerializer
    queryset = HedgeSimulation.objects.all()

    def get_queryset(self):
        """
        Retrieve filtered queryset based on analysis and user.

        Returns:
            QuerySet: Filtered queryset.
        """
        queryset = super().get_queryset()
        analysis_id = self.kwargs.get("analysis_id")
        return queryset.filter(
            analysis_id=analysis_id,
            analysis__user=self.request.user,
            is_deleted=False,
            analysis__is_deleted=False,
        )

    def perform_create(self, serializer):
        """
        Create a new HedgeSimulation and send to the core.

        Args:
            serializer: Serializer instance with data for creating a new instance.
        """
        try:
            send_hedge_to_core(self.request, serializer, **self.kwargs)
        except Exception as e:
            print(e)


@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "delete")
@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "get")
@method_decorator(swagger_auto_schema(tags=["Hedge Simulation"]), "put")
class HedgeIRRRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or destroy a HedgeSimulation instance.

    Attributes:
        serializer_class (class): Serializer for data conversion.
        queryset (QuerySet): Base query set of all HedgeSimulation instances.

    Methods:
        get_object(): Retrieve HedgeSimulation based on provided IDs.
        perform_update(serializer): Update data and send to the core.

    Raises:
        GenericAPIError: Raised if the analysis is not found.

    Usage:
        Used in a RESTful API for managing HedgeSimulation instances.
    """

    serializer_class = HedgeIRRSerializer
    queryset = HedgeSimulation.objects.all()

    def get_object(self):
        """
        Retrieve HedgeSimulation instance based on IDs.

        Returns:
            HedgeSimulation: Retrieved instance.

        Raises:
            GenericAPIError: Raised if analysis is not found.
        """
        try:
            queryset = HedgeSimulation.objects.get(
                hedge_irr_simulation_id=self.kwargs.get("hedge_simulation_id"),
                analysis__pk=self.kwargs.get("analysis_id"),
                analysis__user=self.request.user,
                is_deleted=False,
                analysis__is_deleted=False,
            )
            return queryset
        except ObjectDoesNotExist as e:
            raise GenericAPIError("Analysis Not Found", code=404)

    def perform_update(self, serializer):
        """
        Update data and send to the core.

        Args:
            serializer: Serializer instance with updated data.
        """
        send_hedge_to_core(self.request, serializer, **self.kwargs)
