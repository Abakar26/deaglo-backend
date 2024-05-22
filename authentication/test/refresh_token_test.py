from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class RefreshTokenTest(APITestCase):
    """
    Test case for refreshing access tokens in an API view.
    """

    def setUp(self):
        self.email = "ha@deaglo.com"
        self.password = "daniel25"
        self.user = get_user_model().objects.create_user(
            password=self.password,
            email="ha@deaglo.com",
            city="Houston",
            country="USA",
            is_verified=True,
            first_name="Hafiz",
            last_name="Ahmed",
        )
        self.login_url = reverse("user-login-view")

    def test_refresh_token(self):
        """
        Test the behavior of an API view when refreshing access tokens.
        Sends a request to the user login view to obtain access and refresh tokens.
        Uses the obtained refresh token to request a new access token.
        """
        data = {"email": self.email, "password": self.password}
        login_response = self.client.post(self.login_url, data, format="json")
        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(
            reverse("token-refresh"), {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)
        self.assertNotEqual(
            login_response.data["access"], refresh_response.data["access"]
        )
