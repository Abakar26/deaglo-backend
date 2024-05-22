from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.factory import UserFactory
from authentication.models import TypeUserRole
from organization.factory import OrganizationFactory
from organization.models import Organization


class UpdateAdminOrganizationTest(APITestCase):
    """
    Test case for handling getting organization in an API view.
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

    def test_update_organization_positive(self):
        """
        Test we can update organization (non-deleted) with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_one.organization_id},
            ),
            data=self._build_request(self.organization_one),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        object = Organization.objects.get(pk=self.organization_one.organization_id)
        self._test_response(response.data, object)

    def test_update_organization_positive_deleted(self):
        """
        Test we can update organization (deleted) with admin profile
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_two.organization_id},
            ),
            data=self._build_request(self.organization_two),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        object = Organization.objects.get(pk=self.organization_two.organization_id)
        self._test_response(response.data, object)

    def test_update_organization_forbidden_provider_user(self):
        """
        Test we can not get all organizations with provider account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_one.organization_id},
            ),
            data=self._build_request(self.organization_one),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_organization_forbidden_free_user(self):
        """
        Test we can not get all organizations with free account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_one.organization_id},
            ),
            data=self._build_request(self.organization_one),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_organization_forbidden_premium_user(self):
        """
        Test we can not get all organizations with premium account
        """
        self.client.force_authenticate(user=self.provider_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_one.organization_id},
            ),
            data=self._build_request(self.organization_one),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_organization_forbidden_org_admin_user(self):
        """
        Test we can not get all organizations with org admin account

        """
        self.client.force_authenticate(user=self.org_admin_user)
        response = self.client.put(
            reverse(
                "admin-organization-detail",
                kwargs={"organization_id": self.organization_one.organization_id},
            ),
            data=self._build_request(self.organization_one),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _build_request(self, instance):
        return {
            "name": instance.name + " - edit",
        }

    def _test_response(self, response, instance):
        self.assertEqual(response["organization_id"], str(instance.organization_id))
        self.assertEqual(response["is_deleted"], instance.is_deleted)
        self.assertEqual(response["name"], instance.name)
