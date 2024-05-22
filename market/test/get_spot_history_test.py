from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import SpotHistoryFactory
from market.models import SpotHistory


class GetSpotHistoryTest(APITestCase):
    """
    Test case for handling get spot history in an API view.
    It is designed to test the behavior of an API view when dealing with retrieving the spot history associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Create verified user instances
        2. Create spot history instances where:
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.spot_history_one_user_one = SpotHistoryFactory(user=self.user_one)
        self.spot_history_one_user_two = SpotHistoryFactory(user=self.user_two)

    def test_retrieve_spot_history_detail_user_one(self):
        """
        Test we can retrieve non-deleted spot history for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "spot-history-detail",
                kwargs={
                    "spot_history_id": self.spot_history_one_user_one.spot_history_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        spot_history = SpotHistory.objects.filter(user=self.user_one)
        self.assertEqual(len(spot_history), 2)

        self._test_compare_response_instance(response.data, spot_history.first())

    def _test_compare_response_instance(self, response, instance):
        self.assertEqual(response["duration_months"], instance.duration)
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
