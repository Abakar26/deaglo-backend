from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class SignupTest(APITestCase):
    """
    Test case for user signup in an API view.
    """

    def setUp(self):
        self.data = {
            "email": "ha@deaglo.com",
            "password": "newOgan23423",
            "phone_number": "+11234567890",
            "city": "Houston",
            "state": "TX",
            "zip_code": 123456,
            "country": "USA",
            "first_name": "Hafiz",
            "last_name": "Ahmed",
            "company": "Deaglo",
            "job_title": "Software Engineer",
            "company_type": "TECH",
        }

    def test_signup(self):
        """
        Test the behavior of an API view when signing up a new user.
        Sends a request to the user signup view with provided user information.
        Asserts that the response status code is 201 (Created).
        """
        response = self.client.post(
            reverse("user-signup-view"), self.data, format="json"
        )
        self.assertEqual(response.status_code, 201)
