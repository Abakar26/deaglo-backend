from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import SpotHistoryFactory
from market.models import SpotHistory


class CreateSpotHistoryTest(APITestCase):
    """
    Test case for handling get spot history in an API view.
    It is designed to test the behavior of an API view when dealing with creating the spot history associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Create verified user instances
        2. Creat spot history instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.spot_history_one_user_two = SpotHistoryFactory(user=self.user_two)

        self.request = {
            "base_currency": {
                "code": "EUR",
                "country_name": "European Union",
            },
            "foreign_currency": {
                "code": "USD",
                "country_name": "United States of America",
            },
            "duration_months": 12,
        }

    def test_create_spot_history_user_one(self):
        """
        Test we can create spot history for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse("spot-history-list"),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._test_compare_request_response(self.request, response.data)
        spot_history = SpotHistory.objects.filter(user=self.user_one).first()
        self._test_compare_response_instance(response.data, spot_history)

    def test_create_spot_history_user_two(self):
        """
        Test when user has already has spot history created
        Should return 208 response with latest non deleted spot history
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse("spot-history-list"),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        spot_history = SpotHistory.objects.filter(user=self.user_two)
        self.assertEqual(len(spot_history), 3)
        self._test_compare_request_response(self.request, response.data)

    def _test_compare_request_response(self, request, response):
        self.assertEqual(
            request["base_currency"]["code"], response["base_currency"]["code"]
        )
        self.assertEqual(
            request["base_currency"]["country_name"],
            response["base_currency"]["country_name"],
        )
        self.assertEqual(
            request["foreign_currency"]["code"], response["foreign_currency"]["code"]
        )
        self.assertEqual(
            request["foreign_currency"]["country_name"],
            response["foreign_currency"]["country_name"],
        )
        self.assertEqual(request["duration_months"], response["duration_months"])

    def _test_compare_response_instance(self, response, instance):
        self.assertEqual(response["base_currency"]["code"], instance.base_currency.code)
        self.assertEqual(
            response["base_currency"]["country_name"],
            instance.base_currency.country_name,
        )
        self.assertEqual(
            response["foreign_currency"]["code"], instance.foreign_currency.code
        )
        self.assertEqual(
            response["foreign_currency"]["country_name"],
            instance.foreign_currency.country_name,
        )
        self.assertEqual(response["duration_months"], instance.duration)
