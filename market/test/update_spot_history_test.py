from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from api_gateway.models import TypeCurrency
from authentication.factory import UserFactory
from market.factory import SpotHistoryFactory
from market.models import SpotHistory


class UpdateSpotHistoryTest(APITestCase):
    """
    Test case for handling get spot history in an API view.
    It is designed to test the behavior of an API view when dealing with updating the spot history associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Create verified user instances
        2. Create spot history instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.spot_history_one_user_one = SpotHistoryFactory(user=self.user_one)
        self.spot_history_one_user_two = SpotHistoryFactory(user=self.user_two)

    def test_update_spot_history_user_one(self):
        """
        Test we can update spot history for user one
        """
        request = self._update_request(self.spot_history_one_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "spot-history-detail",
                kwargs={
                    "spot_history_id": self.spot_history_one_user_one.spot_history_id
                },
            ),
            request,
            format="json",
        )

        # Test request matches response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_compare_request_response(request, response.data)

        # Test request matches DB
        spot_history = SpotHistory.objects.filter(user=self.user_one)
        self.assertEqual(len(spot_history), 2)
        self._test_compare_response_instance(response.data, spot_history.first())

        # Test nothing was updated for user two
        spot_history_user_two = SpotHistory.objects.filter(user=self.user_two)
        self.assertEqual(len(spot_history_user_two), 2)
        self.assertEqual(spot_history_user_two.first(), self.spot_history_one_user_two)

    def _test_compare_request_response(self, request, response):
        self.assertEqual(
            request["base_currency"]["code"], response["base_currency"]["code"]
        )
        self.assertEqual(
            request["base_currency"]["country_name"],
            response["base_currency"]["country_name"],
        )
        self.assertEqual(
            request["foreign_currency"]["code"],
            response["foreign_currency"]["code"],
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
            response["foreign_currency"]["code"],
            instance.foreign_currency.code,
        )
        self.assertEqual(
            response["foreign_currency"]["country_name"],
            instance.foreign_currency.country_name,
        )
        self.assertEqual(response["duration_months"], instance.duration)

    def _update_request(self, spot_history):
        updated_base_currency = (
            TypeCurrency.objects.all()
            .exclude(code=spot_history.base_currency.code)
            .order_by("?")
            .first()
        )
        updated_foreign_currency = (
            TypeCurrency.objects.all()
            .exclude(code=spot_history.foreign_currency.code)
            .order_by("?")
            .first()
        )

        return {
            "name": "new name",
            "base_currency": {
                "code": updated_base_currency.code,
                "country_name": updated_base_currency.country_name,
            },
            "foreign_currency": {
                "code": updated_foreign_currency.code,
                "country_name": updated_foreign_currency.country_name,
            },
            "duration_months": spot_history.duration + 1,
        }
