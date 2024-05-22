from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.exceptions import KeyMissingException
from authentication.serializers import UserSerializer
from authentication.swagger.signup import signup_swagger
from authentication.utils import generate_tokens_manually
from authentication.utils import send_otp_via_email, user_init


class SignUpView(APIView):
    """
    API view for user sign-in
    """

    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    @signup_swagger()
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token = generate_tokens_manually(user)
            user_init(user)
            send_otp_via_email(user)
            return Response(token, status=status.HTTP_201_CREATED)

        except KeyError as e:
            raise KeyMissingException(e)
