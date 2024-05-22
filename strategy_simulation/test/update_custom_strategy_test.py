from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from random import randint

from authentication.factory import UserFactory
from strategy_simulation.factory import StrategyFactory
from strategy_simulation.models import Strategy


class UpdateCustomStrategyTest(APITestCase):
    """
    Test case for handling updating custom strategies in an API view.
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

    def test_update_custom_strategy_user_one(self):
        """
        Test we can update the custom strategy for user one
        """
        original_custom_strategy_leg_len = len(
            self.custom_strategy_one_user_one.strategy_leg.filter(is_deleted=False)
        )
        request = self._update_request(self.custom_strategy_one_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_one.strategy_id},
            ),
            request,
            format="json",
        )

        # Verify that the request matches the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(request["name"], response.data["name"])
        self.assertEqual(request["description"], response.data["description"])
        self.assertEqual(len(request["legs"]), len(response.data["legs"]))

        # Verify that the request matches the updated DB object
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_one_user_one.strategy_id
        )
        self.assertEqual(request["name"], db_object.name)
        self.assertEqual(request["description"], db_object.description)
        self.assertEqual(
            len(request["legs"]),
            len(db_object.strategy_leg.filter(is_deleted=False)),
        )
        if original_custom_strategy_leg_len == 1:
            self.assertEqual(
                original_custom_strategy_leg_len,
                len(db_object.strategy_leg.filter(is_deleted=False)),
            )
        else:
            self.assertNotEqual(
                original_custom_strategy_leg_len,
                len(db_object.strategy_leg.filter(is_deleted=False)),
            )

    def test_update_deleted_custom_strategy_user_two(self):
        """
        Test we can not update the deleted custom strategy for user two
        """
        request = self._update_request(self.custom_strategy_one_user_two)
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_two.strategy_id},
            ),
            request,
            format="json",
        )

        # Verify that the request matches the response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify that the request did not update the DB object
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_one_user_two.strategy_id
        )
        self.assertNotEqual(request["name"], db_object.name)
        self.assertNotEqual(request["description"], db_object.description)
        if self.custom_strategy_one_user_two.strategy_leg.all().count() != 1:
            self.assertNotEqual(
                len(request["legs"]),
                len(db_object.strategy_leg.filter(is_deleted=False)),
            )

    def test_update_forbidden_custom_strategy_user_two(self):
        """
        Test we can not update custom strategy for another user
        """
        request = self._update_request(self.custom_strategy_one_user_one)
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_one.strategy_id},
            ),
            request,
            format="json",
        )

        # Verify that the request matches the response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Verify that the request did not update the DB object
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_one_user_one.strategy_id
        )
        self.assertNotEqual(request["name"], db_object.name)
        self.assertNotEqual(request["description"], db_object.description)
        if self.custom_strategy_one_user_one.strategy_leg.all().count() != 1:
            self.assertNotEqual(
                len(request["legs"]),
                len(db_object.strategy_leg.filter(is_deleted=False)),
            )

    def _update_request(self, custom_strategy):
        leg_data = []
        legs_array = custom_strategy.strategy_leg.all()
        if len(legs_array) > 1:
            legs_array = legs_array[1:]
        for leg in legs_array:
            leg_data.append(
                {
                    "is_call": leg.is_call,
                    "is_bought": leg.is_bought,
                    "premium": leg.premium,
                    "leverage": leg.leverage,
                    "strike": leg.strike,
                    "barrier_type": leg.barrier_type,
                    "barrier_level": leg.barrier_level,
                }
            )

        return {
            "name": custom_strategy.name + " - edit",
            "description": custom_strategy.description + " - edit",
            "legs": leg_data,
        }
