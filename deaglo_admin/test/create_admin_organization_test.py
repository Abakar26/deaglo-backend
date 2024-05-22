from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import TypeUserRole
from organization.factory import OrganizationFactory


class CreateAdminOrganizationTest(APITestCase):
    """
    Test case for handling creating organizations in an API view.
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

        self.request = {"name": "Test Organization"}

    def test_create_organization_postive(self):
        """
        Test we can create organization with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("admin-organization-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["is_deleted"])

    def test_create_organization_forbidden_provider_user(self):
        """
        Test we can not create organization with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-organization-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_organization_forbidden_free_user(self):
        """
        Test we can not create organization with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-organization-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_organization_forbidden_premium_user(self):
        """
        Test we can not create organization with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-organization-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_organization_forbidden_org_admin_user(self):
        """
        Test we can not create organization with org admin account

        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.post(
            reverse("admin-organization-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
