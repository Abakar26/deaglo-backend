from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from random import randint

from authentication.factory import UserFactory
from strategy_simulation.models import Strategy


class CreateCustomStrategyTest(APITestCase):
    """
    Test case for handling creating custom strategies in an API view.
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating one verified user instances
        """
        self.user_one = UserFactory()
        self.request = {
            "name": "Test Custom Strategy",
            "description": "Test",
            "legs": [
                {
                    "is_call": True,
                    "is_bought": False,
                    "premium": 1234.56,
                    "leverage": 0.5,
                    "strike": 0.8,
                    "barrier_type": None,
                    "barrier_level": None,
                },
                {
                    "is_call": False,
                    "is_bought": True,
                    "premium": 12346.78,
                    "leverage": 1.0,
                    "strike": 1.2,
                    "barrier_type": None,
                    "barrier_level": None,
                },
                {
                    "is_call": None,
                    "is_bought": True,
                    "premium": 0.0,
                    "leverage": 1.0,
                    "strike": 1.0,
                    "barrier_type": None,
                    "barrier_level": None,
                },
            ],
        }

    def test_all_custom_strategy_user_one(self):
        """
        Test if we can create custom strategies for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse("strategy-list"),
            self.request,
            format="json",
        )

        # Verify that the request and response match
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.request["name"])
        self.assertEqual(response.data["description"], self.request["description"])
        self.assertEqual(len(response.data["legs"]), len(self.request["legs"]))

        # Verify that the request and new DB match
        db_object = Strategy.objects.get(pk=response.data["strategy_id"])
        self.assertEqual(response.data["name"], db_object.name)
        self.assertEqual(response.data["description"], db_object.description)
        self.assertEqual(
            len(response.data["legs"]), db_object.strategy_leg.all().count()
        )
