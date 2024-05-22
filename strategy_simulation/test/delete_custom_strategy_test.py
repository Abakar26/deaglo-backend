from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from random import randint

from authentication.factory import UserFactory
from strategy_simulation.factory import StrategyFactory
from strategy_simulation.models import Strategy


class DeleteCustomStrategyTest(APITestCase):
    """
    Test case for handling deleting custom strategies in an API view.
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

    def test_delete_custom_strategy_user_one(self):
        """
        Test we can delete custom strategy for user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.delete(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_one.strategy_id},
            ),
            format="json",
        )

        # Verify that the db oject is soft deleted in the database
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_one_user_one.strategy_id
        )
        self.assertTrue(db_object.is_deleted)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_deleted_custom_strategy_user_two(self):
        """
        Test we can not delete deleted custom strategy for user two
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.delete(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_one_user_two.strategy_id},
            ),
            format="json",
        )

        # Verify that the db oject is soft deleted in the database
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_one_user_two.strategy_id
        )
        self.assertTrue(db_object.is_deleted)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_forbidden_custom_strategy_user_two(self):
        """
        Test we can not delete custom strategy for another user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.delete(
            reverse(
                "strategy-detail",
                kwargs={"strategy_id": self.custom_strategy_two_user_two.strategy_id},
            ),
            format="json",
        )

        # Verify that the db oject is soft deleted in the database
        db_object = Strategy.objects.get(
            pk=self.custom_strategy_two_user_two.strategy_id
        )
        self.assertFalse(db_object.is_deleted)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
