from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import TypeUserRole
from organization.factory import OrganizationFactory


class CreateAdminUserTest(APITestCase):
    """
    Test case for handling creating users in an API view.
    It is designed to test the behavior of an API view when dealing with user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating each verified user instances (by role)
        """
        # Organization
        self.deaglo_org = OrganizationFactory(name="Deaglo")
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

        self.request = {
            "user_role": "Deaglo Admin",
            "first_name": "John",
            "last_name": "Doe",
            "email": "test@deaglo.com",
            "organization": "Deaglo",
            "city": "New York",
            "country": "United States",
            "password": "Password1234%",
        }

    def test_create_user_positive(self):
        """
        Test we can create users with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_invalid_request_organization(self):
        """
        Test we can not create user with non-existing organization with admin profile
        """
        self.request["organization"] = "Non-Existing Organization"
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_forbidden_provider_user(self):
        """
        Test we can not create users with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_forbidden_free_user(self):
        """
        Test we can not create users with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_forbidden_premium_user(self):
        """
        Test we can not create users with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_forbidden_org_admin_user(self):
        """
        Test we can not create users with org admin account
        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.post(
            reverse("admin-user-list"),
            data=self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
