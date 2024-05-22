from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import TypeUserRole


class DeleteAdminUserTest(APITestCase):
    """
    Test case for handling deleting users in an API view.
    It is designed to test the behavior of an API view when dealing with user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating each verified user instances (by role)
        """
        # User
        self.admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=400)
        )
        self.provider_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=100)
        )
        self.free_user = UserFactory(type_user_role=TypeUserRole.objects.get(level=200))
        self.free_user_deleted = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=200),
            is_deleted=True,
        )
        self.premium_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=210)
        )
        self.org_admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=300)
        )

    def test_delete_user_positive(self):
        """
        Test we can delete users with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_forbidden_provider_user(self):
        """
        Test we can not delete users with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.delete(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden_free_user(self):
        """
        Test we can not delete users with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.delete(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden_premium_user(self):
        """
        Test we can not delete users with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.delete(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden_org_admin_user(self):
        """
        Test we can not delete users with org admin account
        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.delete(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
