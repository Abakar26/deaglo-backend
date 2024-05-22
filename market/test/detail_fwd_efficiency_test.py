from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import FwdEfficiencyFactory


class DetailFwdEfficiencyTest(APITestCase):
    """
    Test case for handling get detail fwd efficiency in an API view.
    It is designed to test the behavior of an API view when dealing with fwd efficiency that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Creating fwd efficiency instances where:
           - One saved belongs to user one
           - One not saved belong to user two
        """

        self.user_one = UserFactory()
        self.user_two = UserFactory()

        self.fwd_efficiency_one_user_one = FwdEfficiencyFactory(
            user=self.user_one, is_deleted=False
        )
        self.fwd_efficiency_one_user_two = FwdEfficiencyFactory(
            user=self.user_two, is_deleted=True
        )

    def test_retrieve_fwd_efficiency_user_one(self):
        """
        Test we can retrieve fwd efficiency for user one
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.get(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_one.fwd_efficiency_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(self.fwd_efficiency_one_user_one.fwd_efficiency_id),
            response.data["fwd_efficiency_id"],
        )

    def test_retrieve_not_saved_fwd_efficiency_user_two(self):
        """
        Test we can retrieve non saved fwd efficiency for user two
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.get(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_two.fwd_efficiency_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(self.fwd_efficiency_one_user_two.fwd_efficiency_id),
            response.data["fwd_efficiency_id"],
        )

    def test_retrieve_forbidden_fwd_efficiency_user_two(self):
        """
        Test we can not retrieve fwd efficiency belonging to another user
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.get(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_one.fwd_efficiency_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
