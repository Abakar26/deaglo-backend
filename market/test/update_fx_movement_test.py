from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
import copy

from api_gateway.models import TypeCurrency
from authentication.factory import UserFactory
from market.factory import FxMovementFactory
from market.models import FxMovement


class UpdateFxMovementTest(APITestCase):
    """
    Test case for handling get fx movement in an API view.
    It is designed to test the behavior of an API view when dealing with updating the fx movement associated with a user
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

    def test_update_fx_movement_user_one(self):
        """
        Test we can update fx movement for user one
        """
        request = self._update_request(self.fx_movement_one_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "fx-movement-detail",
                kwargs={"fx_movement_id": self.fx_movement_one_user_one.fx_movement_id},
            ),
            request,
            format="json",
        )
        # Test request matches response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_compare_request_response(request, response.data)

        # Test request matches DB
        fx_movement = FxMovement.objects.filter(user=self.user_one)
        self.assertEqual(len(fx_movement), 2)
        self._test_compare_response_instance(response.data, fx_movement.first())
        # Verify that user two fx movement is not affected
        fx_movement_user_two = FxMovement.objects.filter(user=self.user_two)
        self.assertEqual(len(fx_movement_user_two), 2)
        self.assertEqual(self.fx_movement_one_user_two, fx_movement_user_two.first())

    def _test_compare_request_response(self, request, response):
        self.assertEqual(request["duration_months"], response["duration_months"])
        request_pairs = sorted(
            request["currency_pairs"],
            key=lambda p: p["base_currency"]["code"] + p["foreign_currency"]["code"],
        )
        response_pairs = sorted(
            response["currency_pairs"],
            key=lambda p: p["base_currency"]["code"] + p["foreign_currency"]["code"],
        )
        for i in range(len(request_pairs)):
            self.assertEqual(
                request_pairs[i]["base_currency"]["code"],
                response_pairs[i]["base_currency"]["code"],
            )
            self.assertEqual(
                request_pairs[i]["base_currency"]["country_name"],
                response_pairs[i]["base_currency"]["country_name"],
            )
            self.assertEqual(
                request_pairs[i]["foreign_currency"]["code"],
                response_pairs[i]["foreign_currency"]["code"],
            )
            self.assertEqual(
                request_pairs[i]["foreign_currency"]["country_name"],
                response_pairs[i]["foreign_currency"]["country_name"],
            )

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

    def _update_request(self, fx_movement):
        updated_base_currency = TypeCurrency.objects.all().order_by("?").first()

        updated_foreign_currency = TypeCurrency.objects.all().order_by("?").first()

        return {
            "name": "new name",
            "currency_pairs": [
                {
                    "base_currency": {
                        "code": updated_base_currency.code,
                        "country_name": updated_base_currency.country_name,
                    },
                    "foreign_currency": {
                        "code": updated_foreign_currency.code,
                        "country_name": updated_foreign_currency.country_name,
                    },
                }
            ],
            "duration_months": fx_movement.duration + 1,
        }
