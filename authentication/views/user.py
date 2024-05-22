from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authentication.serializers import UserSerializer


@method_decorator(
    swagger_auto_schema(
        tags=["User"],
        responses={200: UserSerializer()},
    ),
    name="get",
)
@method_decorator(
    swagger_auto_schema(
        tags=["User"],
        responses={200: UserSerializer()},
    ),
    name="patch",
)
@method_decorator(
    swagger_auto_schema(
        tags=["User"],
    ),
    name="delete",
)
class UserView(APIView):
    """
    API view for retrieving and updating details of the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_dict = UserSerializer(request.user)
        return Response(user_dict.data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"status": "success"}, status=status.HTTP_204_NO_CONTENT)
