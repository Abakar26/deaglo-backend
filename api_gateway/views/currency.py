from api_gateway.models import TypeCurrency
from rest_framework import generics
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from api_gateway.serializers import CurrencySerializer


@method_decorator(swagger_auto_schema(tags=["Currency"]), "get")
class Currency(NonDeletedQuerySetMixin, generics.ListAPIView):
    queryset = TypeCurrency.objects.filter()
    serializer_class = CurrencySerializer
    pagination_class = None

    ctx_args = {
        "analysis": {"is_analysis": True},
        "spot_history": {"is_spot_history": True},
        "fwd_efficiency": {"is_fwd_efficiency": True},
        "fx_movement": {"is_fx_movement": True},
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        currency_type = self.request.query_params.get("ctx")
        if currency_type in self.ctx_args:
            query_arg = self.ctx_args[currency_type]
            return queryset.filter(**query_arg)
        return queryset
