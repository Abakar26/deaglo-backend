from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api_gateway.exceptions import KeyMissingException, GenericAPIError
from authentication.models import User
from authentication.swagger import forgot_password_swagger
from authentication.utils import check_otp, send_otp_via_email
from django.http import Http404


class ForgotPasswordView(APIView):
    """
    API view for handling the "Forgot Password" functionality.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @forgot_password_swagger()
    def post(self, request):
        try:
            email = request.data["email"]
            user = get_object_or_404(User, email=email)
            otp_code = request.data.get("code", None)
            if otp_code:
                result = check_otp(user=user, code=otp_code)
                if result:
                    new_password = request.data.get("new_password")
                    validate_password(new_password, user=user)
                    user.set_password(new_password)
                    user.save()
                    user.otp.delete()
                    return Response(
                        {"status": "success", "message": "password changed"}
                    )
                return Response(
                    {"error": "Incorrect or invalid OTP"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                send_otp_via_email(user)
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Http404:
            raise GenericAPIError(
                "An email will be sent if the account is active and valid.",
                code=status.HTTP_404_NOT_FOUND,
            )
        except KeyError as e:
            raise KeyMissingException(e)
