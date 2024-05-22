from random import random
from urllib.parse import urlencode

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.exceptions import GenericAPIError
from api_gateway.settings.config import (
    LINKEDIN_CLIENT_ID,
)
from authentication.utils import (
    get_redirect_url,
    get_linked_in_response,
    create_user_using_linkedin_profile,
)
from authentication.utils import (
    sign_in_with_linkedin,
    link_linkedin_account,
    delink_linkedin_account,
    verify_otp,
)
from django.contrib.auth import get_user_model


class LinkedInView(APIView):
    """
    This class is used to get  profile data from LinkedIn.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """
        Generate URL for LinkedIn authentication.
        """

        url_type = request.query_params.get("url_type")
        url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": LINKEDIN_CLIENT_ID,
            "redirect_uri": get_redirect_url("auth")
            if url_type == "auth"
            else get_redirect_url("link"),
            "state": str(random() * 100),
            "scope": "openid email profile",
        }
        redirect_url = f"{url}?{urlencode(params)}"
        return Response(redirect_url)

    def post(self, request):
        """
        Signs in user with LinkedIn.
        :param request:
        :return:
        """

        profile_data = get_linked_in_response(request.data["code"], "auth")
        if not (get_user_model().objects.filter(email=profile_data["email"]).exists()):
            create_user_using_linkedin_profile(profile_data)
        sub = profile_data["sub"]

        return Response(sign_in_with_linkedin(sub))


class LinkedinLinkingView(APIView):
    def patch(self, request):
        """Link and Delink LinkedIn account"""
        link = request.data["link"]
        user = request.user
        otp = request.data["otp"]
        if not verify_otp(user, otp):
            raise GenericAPIError(
                "OTP expired",
                {
                    "message": "OTP expired. Please login again and generate a new one",
                },
                400,
            )

        if link:
            code = request.data["code"]
            profile_data = get_linked_in_response(code, "link")
            link_linkedin_account(user, profile_data)
            return Response({"message": "Linkedin account linked successfully"})
        delink_linkedin_account(user)
        return Response({"message": "Linkedin account delinked successfully"})
