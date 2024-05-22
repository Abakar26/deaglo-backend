from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.exceptions import GenericAPIError, KeyMissingException
from authentication.swagger import signin_swagger
from authentication.utils import generate_tokens_manually


class SignInView(APIView):
    """
    API view for user sign-in.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @signin_swagger()
    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]

        except KeyError as e:
            raise KeyMissingException(e)

        user = authenticate(request, email=email, password=password)

        if user and not user.is_deleted:
            login(request, user)
            token = generate_tokens_manually(user)
            verified = {"verified": user.is_verified}
            return Response({**token, **verified}, status=status.HTTP_200_OK)

        else:
            raise GenericAPIError(
                "You have entered an invalid username or password",
                code=status.HTTP_401_UNAUTHORIZED,
            )
