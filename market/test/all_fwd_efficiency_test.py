from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import FwdEfficiencyFactory


class AllFwdEfficiencyTest(APITestCase):
    """
    Test case for handling get fwd efficiency in an API view
    Is is designed to test the behavior of an API view when dealing with retrieving the fwd efficiency associated with a user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Creating fwd efficiency instances where:
           - One saved belongs to user one
           - Three belong to user two (one not saved)
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()

        self.fwd_efficiency_one_user_one = FwdEfficiencyFactory(
            user=self.user_one, is_deleted=False
        )
        self.fwd_efficiency_one_user_two = FwdEfficiencyFactory(
            user=self.user_two, is_deleted=True
        )
        self.fwd_efficiency_two_user_two = FwdEfficiencyFactory(
            user=self.user_two, is_deleted=False
        )
        self.fwd_efficiency_three_user_two = FwdEfficiencyFactory(
            user=self.user_two, is_deleted=False
        )

    def test_all_fwd_efficiency_user_one(self):
        """
        Test we can retrieve saved fwd efficiency for user one
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.get(
            reverse("fwd-efficiency-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIn(
            str(self.fwd_efficiency_one_user_one.fwd_efficiency_id),
            [a["fwd_efficiency_id"] for a in response.data["results"]],
        )

    def test_all_fwd_efficiency_user_two(self):
        """
        Test we can retrieve saved fwd efficiency for user two
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.get(
            reverse("fwd-efficiency-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertNotIn(
            str(self.fwd_efficiency_one_user_two.fwd_efficiency_id),
            [a["fwd_efficiency_id"] for a in response.data["results"]],
        )
