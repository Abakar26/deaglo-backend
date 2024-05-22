from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from random import randint

from authentication.factory import UserFactory
from strategy_simulation.factory import StrategyFactory
from strategy_simulation.models import StrategyLeg
from strategy_simulation.utils.test.get_strategy_from_response import (
    get_custom_strategy_from_response,
)


class AllCustomStrategyTest(APITestCase):
    """
    Test case for handling getting all custom strategies in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted custom strategy that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create custom strategy instances where:
           - One belongs to user one
           - Two belong to user two (one is deleted)
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()

        self.custom_strategy_one_user_one = StrategyFactory(
            created_by_user=self.user_one
        )
        self.custom_strategy_one_user_two = StrategyFactory(
            is_deleted=True, created_by_user=self.user_two
        )
        self.custom_strategy_two_user_two = StrategyFactory(
            created_by_user=self.user_two
        )

    def test_all_custom_strategy_user_one(self):
        """
        Test if we can retrieve non deleted custom strategies for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse("strategy-list"),
            format="json",
        )

        custom_strategies = get_custom_strategy_from_response(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(custom_strategies), 1)
        self.assertIn(
            str(self.custom_strategy_one_user_one.strategy_id),
            [a["strategy_id"] for a in response.data],
        )

        # Verify that the legs are expected
        legs = response.data[0]["legs"]
        expected_legs = list(
            StrategyLeg.objects.filter(strategy=self.custom_strategy_one_user_one)
        )
        self.assertEqual(len(legs), len(expected_legs))

    def test_all_custom_strategy_user_test(self):
        """
        Test if we can retrieve non deleted custom strategies for user two
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse("strategy-list"),
            format="json",
        )

        custom_strategies = get_custom_strategy_from_response(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(custom_strategies), 1)
        self.assertIn(
            str(self.custom_strategy_two_user_two.strategy_id),
            [a["strategy_id"] for a in response.data],
        )
        self.assertNotIn(
            str(self.custom_strategy_one_user_two.strategy_id),
            [a["strategy_id"] for a in response.data],
        )
        # Verify that the legs are expected
        legs = response.data[0]["legs"]
        expected_legs = list(
            StrategyLeg.objects.filter(strategy=self.custom_strategy_two_user_two)
        )
        self.assertEqual(len(legs), len(expected_legs))
