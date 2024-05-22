from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.models import FwdEfficiency


class CreateFwdEfficiencyTest(APITestCase):
    """
    Test case for handling create fwd efficiency in an API view
    Is is designed to test the behavior of an API view when dealing with creating the fwd efficiency associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating one verified user instances
        """
        self.user_one = UserFactory()
        self.request = {
            "name": "new name",
            "base_currency": {
                "code": "EUR",
                "country_name": "European Union",
            },
            "foreign_currency": {
                "code": "USD",
                "country_name": "United States of America",
            },
            "duration_months": 24,
        }

    def test_create_fwd_efficiency_user_one(self):
        """
        Test we can create non-saved fwd efficiency for user one
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.post(
            reverse("fwd-efficiency-list"),
            self.request,
            format="json",
        )

        # Check if the response is as expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.request["name"])
        self.assertEqual(
            response.data["base_currency"]["code"],
            self.request["base_currency"]["code"],
        )
        self.assertEqual(
            response.data["base_currency"]["country_name"],
            self.request["base_currency"]["country_name"],
        )
        self.assertEqual(
            response.data["foreign_currency"]["code"],
            self.request["foreign_currency"]["code"],
        )
        self.assertEqual(
            response.data["foreign_currency"]["country_name"],
            self.request["foreign_currency"]["country_name"],
        )
        self.assertEqual(
            response.data["duration_months"], self.request["duration_months"]
        )

        # Check if new DB object is as expected
        new_object = FwdEfficiency.objects.get(pk=response.data["fwd_efficiency_id"])
        self.assertEqual(new_object.name, self.request["name"])
        self.assertEqual(
            new_object.base_currency.code, self.request["base_currency"]["code"]
        )
        self.assertEqual(
            new_object.base_currency.country_name,
            self.request["base_currency"]["country_name"],
        )
        self.assertEqual(
            new_object.foreign_currency.code, self.request["foreign_currency"]["code"]
        )
        self.assertEqual(
            new_object.foreign_currency.country_name,
            self.request["foreign_currency"]["country_name"],
        )
        self.assertEqual(new_object.duration, self.request["duration_months"])
        self.assertEqual(new_object.is_deleted, False)
