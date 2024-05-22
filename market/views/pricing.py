from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.settings import FENICS_CLIENT
from market.serializers import (
    SpotRateRequestSerializer,
    SpotRateResponseSerializer,
    ForwardRateRequestSerializer,
    ForwardRateResponseSerializer,
    OptionPriceRequestSerializer,
    OptionPriceResponseSerializer,
)


@method_decorator(
    swagger_auto_schema(
        tags=["Pricing"],
        responses={200: SpotRateResponseSerializer()},
        request_body=SpotRateRequestSerializer,
    ),
    "post",
)
class SpotRateView(APIView):
    def post(self, request):
        request_serializer = SpotRateRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        response_data = FENICS_CLIENT.vanilla_pricing_query(
            **request_serializer.validated_data
        )

        if "errors" in response_data:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = SpotRateResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    swagger_auto_schema(
        tags=["Pricing"],
        responses={200: ForwardRateResponseSerializer()},
        request_body=ForwardRateRequestSerializer,
    ),
    "post",
)
class ForwardRateView(APIView):
    def post(self, request):
        request_serializer = ForwardRateRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        response_data = FENICS_CLIENT.vanilla_pricing_query(
            **request_serializer.validated_data
        )

        if "errors" in response_data:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = ForwardRateResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@method_decorator(
    swagger_auto_schema(
        tags=["Pricing"],
        responses={200: OptionPriceResponseSerializer()},
        request_body=OptionPriceRequestSerializer,
        manual_parameters=[
            openapi.Parameter(
                "include_greeks",
                openapi.IN_QUERY,
                type="bool",
                description="Indicates whether to include option greeks data in the response",
                required=False,
                default=False,
            ),
        ],
    ),
    "post",
)
class OptionPriceView(APIView):
    def post(self, request):
        serializer = OptionPriceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "barrier_type" in request.data and "barrier_level" in request.data:
            response_data = FENICS_CLIENT.barrier_pricing_query(
                **serializer.validated_data
            )
        else:
            response_data = FENICS_CLIENT.vanilla_pricing_query(
                **serializer.validated_data
            )

        if "errors" in response_data:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = OptionPriceResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        response_obj = response_serializer.data
        include_greeks = request.query_params.get(
            "include_greeks", "false"
        ).lower() in ["true", "1"]
        if not include_greeks:
            response_obj.pop("greeks")
        return Response(response_obj, status=status.HTTP_200_OK)
