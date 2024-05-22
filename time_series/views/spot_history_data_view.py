from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from time_series.serializers import SpotHistoryDataRequestSerializer


@method_decorator(
    swagger_auto_schema(
        tags=["Time Series"],
        responses={200: SpotHistoryDataRequestSerializer()},
        request_body=SpotHistoryDataRequestSerializer,
    ),
    "post",
)
class SpotHistoryDataAPIView(APIView):
    def post(self, request):
        serializer = SpotHistoryDataRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
