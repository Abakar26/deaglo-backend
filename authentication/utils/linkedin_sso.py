from typing import Literal

import requests
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from api_gateway.exceptions import GenericAPIError
from api_gateway.settings import (
    LINKEDIN_REDIRECT_URI_AUTH,
    LINKEDIN_REDIRECT_URI_LINK,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
)
from .otp_utils import verify_otp
from .tokens_utils import generate_tokens_manually
from ..models import SSO


def sign_in_with_linkedin(sub: str):
    user = get_object_or_404(get_user_model(), sso__linkedin_id=sub)
    token = generate_tokens_manually(user)
    return {**token, "verified": user.is_verified}


def create_user_using_linkedin_profile(profile: dict):
    if (
        get_user_model().objects.filter(email=profile["email"]).exists()
        or not profile["email_verified"]
    ):
        return
    user = get_user_model().objects.create_user(
        email=profile["email"],
        first_name=profile["given_name"],
        last_name=profile["family_name"],
    )
    SSO.objects.create(user=user, linkedin_id=profile["sub"])
    return user


def link_linkedin_account(user, profile_data: dict):
    if not profile_data["email_verified"]:
        raise GenericAPIError(
            "Email is not verified in LinkedIn",
            {"message": "Unverified LinkedIn Email can't use"},
            400,
        )
    sso = SSO.objects.create(user=user, linkedin_id=profile_data["sub"])
    return sso


def delink_linkedin_account(user):
    user.sso.delete()
    return


def get_redirect_url(uri_type: Literal["auth", "link"]) -> str:
    match uri_type:
        case "auth":
            return LINKEDIN_REDIRECT_URI_AUTH
        case "link":
            return LINKEDIN_REDIRECT_URI_LINK
        case _:
            raise GenericAPIError(
                "Invalid uri_type",
                {"message": "Invalid uri_type"},
                400,
            )


def get_linked_in_response(code: str, uri_type: Literal["auth", "link"]):
    """
    Use to fetch user profile from LinkedIn server
    :param code:
    :return:
    """
    access_token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": get_redirect_url(uri_type),
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }

    response = requests.post(access_token_url, data=params).json()
    access_code = response.get("access_token")
    if access_code:
        profile_url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_code}"}
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()
        return profile_data
    else:
        raise GenericAPIError(
            "Expired code",
            {"message": "Try again authentication code is expired"},
            400,
        )
