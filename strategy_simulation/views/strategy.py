from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin
from strategy_simulation.models import Strategy
from strategy_simulation.serializers import StrategySerializer


@method_decorator(swagger_auto_schema(tags=["Strategy"]), "get")
@method_decorator(swagger_auto_schema(tags=["Strategy"]), "post")
class StrategyListCreateAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.ListCreateAPIView
):
    """API view for retrieving list of default strategy created by Deaglo and custom strategies created by authenticated user"""

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer

    def __init__(self, **kwargs):
        super().__init__(user_field="created_by_user", **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["strategy_leg__is_deleted"] = False
        context["user"] = self.request.user
        return context

    # TODO: Can you query param for getting default / custom only
    def list(self, request, *args, **kwargs):
        response = super().list(self, request, *args, **kwargs).data
        default_strategy_query_set = Strategy.objects.default_strategy(is_deleted=False)
        default_strategy = self.get_serializer(
            default_strategy_query_set, many=True
        ).data
        response = response["results"] + default_strategy
        return Response(response)


@method_decorator(swagger_auto_schema(tags=["Strategy"]), "get")
@method_decorator(swagger_auto_schema(tags=["Strategy"]), "put")
@method_decorator(swagger_auto_schema(tags=["Strategy"]), "delete")
@method_decorator(swagger_auto_schema(auto_schema=None), "patch")
class StrategyRetrieveUpdateDestroyAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """API view for retrieving default strategy created by Deaglo custom strategy created by authenticated user"""

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    lookup_field = "strategy_id"

    def __init__(self, **kwargs):
        super().__init__(
            user_field="created_by_user",
            include_user_none=True,
            **kwargs,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["strategy_leg__is_deleted"] = False
        context["user"] = self.request.user
        return context

    def get_queryset(self):
        """
        Override the get_queryset method to adjust the query based on the request method.
        For retrieve ('GET') requests, include default and custom strategies.
        For update ('PUT') and delete ('DELETE') requests, include only custom strategies.
        """
        if self.request.method == "GET":
            self.include_user_none = True
        else:
            self.include_user_none = False
        return super().get_queryset()

    def perform_destroy(self, instance):
        instance.delete()

    def patch(self, request, *args, **kwargs):
        return Response(
            {"error": "Partial update (PATCH) not implemented."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
