from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from django.core.exceptions import ValidationError

from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin
from market.models import FxMovement
from market.serializers import FxMovementSerializer


@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "get")
@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "post")
class FxMovementListCreateAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of fx movements saved by authenticated user"""

    queryset = FxMovement.objects.filter()
    serializer_class = FxMovementSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "get")
@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "put")
@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Fx Movement"]), "delete")
class FxMovementRetrieveUpdateDestroyAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for retrieving and updating fx movement for authenticated user"""

    queryset = FxMovement.objects.filter()
    serializer_class = FxMovementSerializer
    lookup_field = "fx_movement_id"

    def delete(self, request: Request, *args, **kwargs):
        default_fx_movement_id = FxMovement.objects.get(
            user=request.user, is_default=True
        )
        if self.kwargs.get("fx_movement_id") == default_fx_movement_id:
            raise ValidationError("Cannot delete default FX Movement")

        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()
