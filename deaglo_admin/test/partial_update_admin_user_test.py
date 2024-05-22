from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import User, TypeUserRole
from organization.factory import OrganizationFactory


class PartialUpdateAdminUserTest(APITestCase):
    """
    Test case for handling partially updating user in an API view.
    It is designed to test the behavior of an API view when dealing with user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating each verified user instances (by role)
        """
        # Organization
        self.deaglo_org = OrganizationFactory(name="Deaglo")
        self.fund_org = OrganizationFactory(name="Fund Capital Management")
        # User
        self.admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=400),
            organization=self.deaglo_org,
        )
        self.provider_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=100),
            organization=self.fund_org,
        )
        self.free_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=200),
            organization=self.fund_org,
        )
        self.free_user_deleted = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=200),
            is_deleted=True,
            organization=self.fund_org,
        )
        self.premium_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=210),
            organization=self.fund_org,
        )
        self.org_admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=300),
            organization=self.fund_org,
        )

    def test_partial_update_user_positive(self):
        """
        Test we can partially update user with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            reverse(
                "admin-user-detail", kwargs={"user_id": self.free_user_deleted.user_id}
            ),
            data={"is_deleted": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        object = User.objects.get(pk=self.free_user_deleted.user_id)
        self._test_response(response.data, object)

    def test_partial_update_user_positive_deleted_target(self):
        """
        Test we can partially update deleted user with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        object = User.objects.get(pk=self.free_user.user_id)
        self._test_response(response.data, object)

    def test_partial_update_user_negative_invalid_organization(self):
        """
        Test we can not update user to non existing organization
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"organization": "Non-Existing Organization"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_user_forbidden_provider_user(self):
        """
        Test we can not update user with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user_forbidden_free_user(self):
        """
        Test we can not update user with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user_forbidden_premium_user(self):
        """
        Test we can not update user with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_user_forbidden_org_admin_user(self):
        """
        Test we can not update user with org admin account
        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.patch(
            reverse("admin-user-detail", kwargs={"user_id": self.free_user.user_id}),
            data={"is_deleted": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _test_response(self, response, instance):
        self.assertEqual(response["is_deleted"], instance.is_deleted)
        self.assertEqual(response["is_verified"], instance.is_verified)
        self.assertEqual(response["is_active"], instance.is_active)
        self.assertEqual(response["first_name"], instance.first_name)
        self.assertEqual(response["last_name"], instance.last_name)
        self.assertEqual(response["email"], instance.email)
        self.assertEqual(response["city"], instance.city)
        self.assertEqual(response["country"], instance.country)
        self.assertEqual(response["organization"], instance.organization.name)
