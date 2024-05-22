from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class MissingCredentialsTest(APITestCase):
    """
    Test case for handling authentication failure with missing credentials in an API view.
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
        self.login_url = reverse("user-login-view")

    def test_missing_credentials(self):
        """
        Test the behavior of an API view when authentication fails with missing credentials.
        """
        data = {}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
