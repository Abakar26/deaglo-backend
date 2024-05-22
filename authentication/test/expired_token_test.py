from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class ExpiredTokenTest(APITestCase):
    """
    Test case for handling expired tokens in an API view.
    It is designed to test the behavior of an API view when authentication fails due to an expired token.
    """

    def setUp(self):
        """Set up the test environment by creating a user instance with a verified account."""
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

    def test_expired_token(self):
        """
         Test the behavior of an API view when authentication fails with an expired token.
        Generates an expired token and sends a request to the specified API view using this token.
        Asserts that the response status code is 405 (Method Not Allowed).
        """
        from datetime import timedelta

        # Test authentication failure with an expired token
        refresh = RefreshToken.for_user(self.user)
        refresh.access_token.set_exp(
            lifetime=timedelta(seconds=-100)
        )  # Set token expiration to the past
        response = self.client.post(
            reverse("get-user-view"),
            headers={"Authorization": "Bearer " + str(refresh.access_token)},
            format="json",
        )
        self.assertEqual(response.status_code, 405)
