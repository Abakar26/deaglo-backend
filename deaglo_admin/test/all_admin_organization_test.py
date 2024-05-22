from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import TypeUserRole
from organization.factory import OrganizationFactory


class AllAdminOrganizationTest(APITestCase):
    """
    Test case for handling getting all organizations in an API view.
    It is designed to test the behavior of an API view when dealing with organization
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating each verified user instances (by role)
        2. Create organization instances
        """
        # User
        self.admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=400)
        )
        self.provider_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=100)
        )
        self.free_user = UserFactory(type_user_role=TypeUserRole.objects.get(level=200))
        self.premium_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=210)
        )
        self.org_admin_user = UserFactory(
            type_user_role=TypeUserRole.objects.get(level=300)
        )
        # Organization
        self.organization_one = OrganizationFactory()
        self.organization_two = OrganizationFactory(is_deleted=True)

    def test_all_organization_positive(self):
        """
        Test we can get all organizations (deleted and non-deleted) with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(
            reverse("admin-organization-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_all_organization_forbidden_provider_user(self):
        """
        Test we can not get all organizations with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.get(
            reverse("admin-organization-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_organization_forbidden_free_user(self):
        """
        Test we can not get all organizations with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.get(
            reverse("admin-organization-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_organization_forbidden_premium_user(self):
        """
        Test we can not get all organizations with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.get(
            reverse("admin-organization-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_all_organization_forbidden_org_admin_user(self):
        """
        Test we can not get all organizations with org admin account

        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.get(
            reverse("admin-organization-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
