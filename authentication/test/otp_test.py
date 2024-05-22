from datetime import timedelta

from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.factory import UserFactory


class OTPTest(APITestCase):
    """
    Test case for obtaining OTP after user signup in an API view.
    """

    def setUp(self):
        """
        Set up the test environment by creating a dictionary with user information.
        """

        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_get_otp(self):
        """
        Test the behavior of an API view when obtaining OTP after user signup.
        """
        response = self.client.get(
            reverse("get-otp-view"),
            format="json",
        )
        self.assertEqual(response.status_code, 200, "GET OTP")
        response = self.client.get(
            reverse("get-otp-view"),
            format="json",
        )
        self.assertEqual(response.status_code, 200, "GET OTP twice")

    def test_expired(self):
        self.client.get(reverse("get-otp-view"), format="json")
        self.user.otp.expired_at = self.user.otp.expired_at - timedelta(days=1)
        self.user.otp.save()
        response = self.client.post(
            reverse("otp-verify-view"), {"otp_code": self.user.otp.code}, format="json"
        )
        self.assertEqual(response.status_code, 400, "OTP Expired")

    def test_used_otp(self):
        self.client.get(reverse("get-otp-view"), format="json")
        otp = self.user.otp.code
        response = self.client.post(
            reverse("otp-verify-view"), {"otp_code": otp}, format="json"
        )
        self.assertEqual(response.status_code, 200, "OTP verified")
        response = self.client.post(
            reverse("otp-verify-view"), {"otp_code": otp}, format="json"
        )
        self.assertEqual(response.status_code, 404, "OTP not found")
