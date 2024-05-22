from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.exceptions import KeyMissingException
from authentication.swagger import verify_otp_swagger
from authentication.utils import verify_otp


class VerifyOtpView(APIView):
    """
    API view for verifying a One-Time Password (OTP) for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @verify_otp_swagger()
    def post(self, request):
        try:
            user = request.user
            otp_code = request.data["otp_code"]
        except KeyError as e:
            raise KeyMissingException(e)
        verify_otp(user=user, code=otp_code)
        return Response({"status": "success"})
