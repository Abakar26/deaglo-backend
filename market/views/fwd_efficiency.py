from rest_framework import generics
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.request import Request
from django.core.exceptions import ValidationError

from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin
from market.models import FwdEfficiency
from market.serializers import FwdEfficiencySerializer


@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "get")
@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "post")
class FwdEfficiencyListCreateAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of fwd efficiencies saved by authenticated user"""

    queryset = FwdEfficiency.objects.filter()
    serializer_class = FwdEfficiencySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "get")
@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "put")
@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Fwd Efficiency"]), "delete")
class FwdEfficiencyRetrieveUpdateDestroyAPIView(
    UserQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for retrieving fwd efficiency saved by authenticated user"""

    queryset = FwdEfficiency.objects.all()
    serializer_class = FwdEfficiencySerializer
    lookup_field = "fwd_efficiency_id"

    def delete(self, request: Request, *args, **kwargs):
        default_fwd_efficiency_id = FwdEfficiency.objects.get(
            user=request.user, is_default=True
        )
        if self.kwargs.get("fwd_efficiency_id") == default_fwd_efficiency_id:
            raise ValidationError("Cannot delete default FWD Efficiency")

        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()
