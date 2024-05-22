from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
import copy

from authentication.factory import UserFactory
from market.factory import FxMovementFactory
from market.models import FxMovement


class CreateFxMovementTest(APITestCase):
    """
    Test case for handling get fx movement in an API view.
    It is designed to test the behavior of an API view when dealing with creating the fx movement associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Create verified user instances
        2. Create fx movement instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.fx_movement_one_user_two = FxMovementFactory(user=self.user_two)

        self.request = {
            "currency_pairs": [
                {
                    "base_currency": {
                        "code": "USD",
                        "country_name": "United States of America",
                    },
                    "foreign_currency": {
                        "code": "EUR",
                        "country_name": "European Union",
                    },
                },
                {
                    "base_currency": {
                        "code": "USD",
                        "country_name": "United States of America",
                    },
                    "foreign_currency": {"code": "BRL", "country_name": "Brazil"},
                },
            ],
            "duration_months": 24,
        }

    def test_create_fx_movement_user_one(self):
        """
        Test we can create fx movement for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse("fx-movement-list"),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._test_compare_request_response(self.request, response.data)
        fx_movement = FxMovement.objects.filter(user=self.user_one)
        self._test_compare_response_instance(response.data, fx_movement.first())

    def test_create_fx_movement_user_two(self):
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse("fx-movement-list"),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        fx_movement = FxMovement.objects.filter(user=self.user_two)
        self.assertEqual(len(fx_movement), 3)
        self.assertEqual(self.fx_movement_one_user_two, fx_movement[1])

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

    def _test_compare_response_instance(self, response, instance: FxMovement):
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
