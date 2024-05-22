from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.utils import send_otp_via_email
from authentication.swagger import get_otp_swagger
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class GetOtpView(APIView):
    """
    API view for sending a One-Time Password (OTP) via email to an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @get_otp_swagger()
    def get(self, request):
        user = request.user
        if send_otp_via_email(user):
            return Response({"status": "success"})
        return Response(
            {"error": "Service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
