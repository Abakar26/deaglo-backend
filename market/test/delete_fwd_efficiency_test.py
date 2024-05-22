from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from market.factory import FwdEfficiencyFactory
from market.models import FwdEfficiency


class DeleteFwdEfficiencyTest(APITestCase):
    """
    Test case for handling deleting fwd efficiency in an API view.
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

    def test_delete_saved_fwd_efficiency_user_one(self):
        """
        Test we can delete saved fwd efficiency for user one
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.delete(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_one.fwd_efficiency_id
                },
            ),
            format="json",
        )

        # Verify that the db object was soft deleted as expected
        db_object = FwdEfficiency.objects.get(
            pk=self.fwd_efficiency_one_user_one.fwd_efficiency_id
        )
        self.assertTrue(db_object.is_deleted)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_saved_fwd_efficiency_user_two(self):
        """
        Test we can delete non saved fwd efficiency for user two (this wouldn't happen in rl)
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_two.fwd_efficiency_id
                },
            ),
            format="json",
        )

        # Verify that the db object was soft deleted as expected (object was already soft deleted in the past)
        db_object = FwdEfficiency.objects.get(
            pk=self.fwd_efficiency_one_user_two.fwd_efficiency_id
        )
        self.assertTrue(db_object.is_deleted)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_forbidden_fwd_efficiency_user_two(self):
        """
        Test we can not delete fwd efficiency belonging to another user
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_one.fwd_efficiency_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
