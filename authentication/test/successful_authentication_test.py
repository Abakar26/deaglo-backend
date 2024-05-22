from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class SuccessfulAuthenticationTest(APITestCase):
    """
    Test case for successful user authentication in an API view.
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

    def test_successful_authentication(self):
        """
         Test the behavior of an API view when a user successfully logs in.
        Sends a request to the user login view with valid credentials.
        Asserts that the response status code is 200 (OK) and contains both access and refresh tokens.
        """
        data = {"email": self.email, "password": self.password}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
