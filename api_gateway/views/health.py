from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class Health(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(status=200)
