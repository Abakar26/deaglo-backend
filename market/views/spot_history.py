from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from django.core.exceptions import ValidationError

from market.models import SpotHistory
from market.serializers import SpotHistorySerializer
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin


@method_decorator(swagger_auto_schema(tags=["Spot History"]), "get")
@method_decorator(swagger_auto_schema(tags=["Spot History"]), "post")
class SpotHistoryListCreateAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of spot histories saved by authenticated user"""

    queryset = SpotHistory.objects.filter()
    serializer_class = SpotHistorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(swagger_auto_schema(tags=["Spot History"]), "get")
@method_decorator(swagger_auto_schema(tags=["Spot History"]), "put")
@method_decorator(swagger_auto_schema(tags=["Spot History"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Spot History"]), "delete")
class SpotHistoryRetrieveUpdateDestroyAPIView(
    NonDeletedQuerySetMixin,
    UserQuerySetMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    """
    API view for spot history
    Creates one if it does not exist for authenticated user
    Retrieves one if authenticated user already has one
    """

    queryset = SpotHistory.objects.all()
    serializer_class = SpotHistorySerializer
    lookup_field = "spot_history_id"

    def delete(self, request: Request, *args, **kwargs):
        default_spot_history_id = SpotHistory.objects.get(
            user=request.user, is_default=True
        )
        if self.kwargs.get("fx_movement_id") == default_spot_history_id:
            raise ValidationError("Cannot delete default Spot History")

        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()
