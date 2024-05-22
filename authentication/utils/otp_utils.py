import random

from django.template.loader import render_to_string

from api_gateway.exceptions import GenericAPIError
from api_gateway.settings import AWS
from authentication.models import OTP, User


def _generate_otp(user: User):
    """
    Generate a new OTP for the given user, deleting any existing OTPs.
    Returns the newly created OTP instance.
    """
    otp = OTP.objects.filter(user=user)
    if otp.exists():
        otp.delete()
    return OTP.objects.create(user=user, code=random.randint(100000, 999999))


def send_otp_via_email(user: User):
    """
    Generate and send an OTP to the user via email.
        Returns True if the email is sent successfully, False otherwise.
    """
    otp_instance = _generate_otp(user)
    subject = "Your OTP for Two-Factor Authentication"
    body = render_to_string(
        "authentication/otp.html", {"otp": otp_instance.code, "user_name": user.name}
    )
    recipient = user.email
    return AWS.ses.send_email(subject, body, recipient, "Html")


def verify_otp(user: User, code: int):
    """
    Verify the provided OTP code for the user.

    Args:
        user (User): The user for whom the OTP code is being verified.
        code (int): The OTP code to be verified.
    Raises:
        GenericAPIError: If the code is invalid or expired.
    """
    otp_entry = OTP.objects.filter(user=user, code=code).first()

    if not otp_entry:
        raise GenericAPIError("Invalid OTP", code=404)

    if otp_entry.is_expired:
        raise GenericAPIError("OTP expired", code=400)

    user.is_verified = True
    user.save()
    otp_entry.delete()
    return True


def check_otp(user: User, code):
    """
    Check the validity of the provided OTP code for the user.
        Returns True if the code is valid and not expired, False otherwise.
    """
    result = OTP.objects.filter(user=user, code=code)
    if result.exists() and not result.first().is_expired:
        return True
    elif result.exists() and result.first().is_expired:
        result.delete()
    return False
