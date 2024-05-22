from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import FxMovementFactory
from market.models import FxMovement


class GetFxMovementTest(APITestCase):
    """
    Test case for handling get fx movement in an API view.
    It is designed to test the behavior of an API view when dealing with retrieving the fx movement associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Create verified user instances
        2. Create fx movement instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.fx_movement_one_user_one = FxMovementFactory(user=self.user_one)
        self.fx_movement_one_user_two = FxMovementFactory(user=self.user_two)

    def test_retrieve_fx_movement_user_one(self):
        """
        Test we can retrieve non-deleted fx movement for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "fx-movement-detail",
                kwargs={"fx_movement_id": self.fx_movement_one_user_one.fx_movement_id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fx_movement = FxMovement.objects.filter(user=self.user_one)
        self.assertEqual(len(fx_movement), 2)
        self._test_compare_response_instance(response.data, fx_movement.first())

    def _test_compare_response_instance(self, response, instance):
        self.assertEqual(response["duration_months"], instance.duration)
        response_pairs = sorted(
            response["currency_pairs"],
            key=lambda p: p["base_currency"]["code"] + p["foreign_currency"]["code"],
        )
        instance_pairs = sorted(
            instance.currency_pairs.all(),
            key=lambda p: p.base_currency.code + p.foreign_currency.code,
        )
        for i in range(len(response_pairs)):
            self.assertEqual(
                response_pairs[i]["base_currency"]["code"],
                instance_pairs[i].base_currency.code,
            )
            self.assertEqual(
                response_pairs[i]["base_currency"]["country_name"],
                instance_pairs[i].base_currency.country_name,
            )
            self.assertEqual(
                response_pairs[i]["foreign_currency"]["code"],
                instance_pairs[i].foreign_currency.code,
            )
            self.assertEqual(
                response_pairs[i]["foreign_currency"]["country_name"],
                instance_pairs[i].foreign_currency.country_name,
            )
