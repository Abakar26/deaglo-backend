from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from strategy_simulation.factory import StrategyFactory
from strategy_simulation.models import StrategyLeg


class DetailCustomStrategyTest(APITestCase):
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

    def test_detail_custom_strategy_user_one(self):
        """
        Test we can retrieve custom strategy for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_one.strategy_id},
            ),
            format="json",
        )

        # Verify that the response matches the object
        db_object = StrategyLeg.objects.filter(
            strategy=self.custom_strategy_one_user_one
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.custom_strategy_one_user_one.name)
        self.assertEqual(
            response.data["description"], self.custom_strategy_one_user_one.description
        )
        self.assertEqual(len(response.data["legs"]), len(db_object))

    def test_detail_deleted_custom_strategy_user_two(self):
        """
        Test we can not retrieve deleted custom strategy for user two
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_two.strategy_id},
            ),
            format="json",
        )

        # Verify that the response matches the object
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn("name", response.data)

    def test_detail_forbidden_custom_strategy_user_two(self):
        """
        Test we can not retrieve custom strategy for another user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_two_user_two.strategy_id},
            ),
            format="json",
        )

        # Verify that the response matches the object
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn("name", response.data)
