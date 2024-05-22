from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from analysis.models import Analysis, TypeCategory
from authentication.factory import UserFactory
from api_gateway.models import TypeCurrency


class UpdateAnalysisTest(APITestCase):
    """
    Test case for handling updating analysis in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted analysis that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Creating three analysis instances where
           - One deleted analysis belongs to user one
           - One non deleted belongs to user one
           - Two non deleted belongs to user two
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()

        self.deleted_analysis_user_one = AnalysisFactory(
            user=self.user_one, is_deleted=True
        )
        self.non_deleted_analysis_user_one = AnalysisFactory(
            user=self.user_one, is_deleted=False
        )
        self.non_deleted_analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=False
        )
        self.non_deleted_analysis_two_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=False
        )

    def test_update_non_deleted_analysis_user_one(self):
        """
        Ensure we can update non-deleted analysis for user one via patch
        """
        request = self._create_update_request(self.non_deleted_analysis_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.non_deleted_analysis_user_one.analysis_id},
            ),
            request,
            format="json",
        )

        # Ensure that the request and response match
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(self.non_deleted_analysis_user_one.analysis_id),
            response.data["analysis_id"],
        )
        self.assertEqual(
            request["name"],
            response.data["name"],
        )
        self.assertEqual(
            request["category"],
            response.data["category"],
        )
        self.assertEqual(
            request["base_currency"]["code"],
            response.data["base_currency"]["code"],
        )
        self.assertEqual(
            request["base_currency"]["country_name"],
            response.data["base_currency"]["country_name"],
        )
        self.assertEqual(
            request["foreign_currency"]["code"],
            response.data["foreign_currency"]["code"],
        )
        self.assertEqual(
            request["foreign_currency"]["country_name"],
            response.data["foreign_currency"]["country_name"],
        )

        # Ensure that the request and DB object match
        updated_analysis = Analysis.objects.get(
            analysis_id=self.non_deleted_analysis_user_one.analysis_id
        )
        self.assertEqual(
            request["name"],
            updated_analysis.name,
        )
        self.assertEqual(
            request["category"],
            updated_analysis.type_category.name,
        )
        self.assertEqual(
            request["base_currency"]["code"],
            updated_analysis.base_currency.code,
        )
        self.assertEqual(
            request["foreign_currency"]["code"],
            updated_analysis.foreign_currency.code,
        )
        self.assertEqual(
            request["base_currency"]["country_name"],
            updated_analysis.base_currency.country_name,
        )
        self.assertEqual(
            request["foreign_currency"]["country_name"],
            updated_analysis.foreign_currency.country_name,
        )

    def test_update_deleted_analysis_user_one(self):
        """
        Ensure we can not update deleted analysis for user one.
        """
        request = self._create_update_request(self.deleted_analysis_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.deleted_analysis_user_one.analysis_id},
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Ensure that none of the data was updated
        self.assertNotEqual(
            request["name"],
            self.deleted_analysis_user_one.name,
        )
        self.assertNotEqual(
            request["category"],
            self.deleted_analysis_user_one.type_category.name,
        )
        self.assertNotEqual(
            request["base_currency"]["code"],
            self.deleted_analysis_user_one.base_currency.code,
        )
        self.assertNotEqual(
            request["foreign_currency"]["code"],
            self.deleted_analysis_user_one.foreign_currency.code,
        )
        self.assertNotEqual(
            request["base_currency"]["country_name"],
            self.deleted_analysis_user_one.base_currency.country_name,
        )
        self.assertNotEqual(
            request["foreign_currency"]["country_name"],
            self.deleted_analysis_user_one.foreign_currency.country_name,
        )

    def test_update_forbidden_analysis_user_one(self):
        """
        Ensure we can not update user two analysis for user one.
        """
        request = self._create_update_request(self.non_deleted_analysis_one_user_two)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_one_user_two.analysis_id
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Ensure that none of the data was updated
        self.assertNotEqual(
            request["name"],
            self.non_deleted_analysis_one_user_two.name,
        )
        self.assertNotEqual(
            request["category"],
            self.non_deleted_analysis_one_user_two.type_category.name,
        )
        self.assertNotEqual(
            request["base_currency"]["code"],
            self.non_deleted_analysis_one_user_two.base_currency.code,
        )
        self.assertNotEqual(
            request["foreign_currency"]["code"],
            self.non_deleted_analysis_one_user_two.foreign_currency.code,
        )
        self.assertNotEqual(
            request["base_currency"]["country_name"],
            self.non_deleted_analysis_one_user_two.base_currency.country_name,
        )
        self.assertNotEqual(
            request["foreign_currency"]["country_name"],
            self.non_deleted_analysis_one_user_two.foreign_currency.country_name,
        )

    def test_update_non_deleted_analysis_one_user_two(self):
        """
        Ensure we can update correct non-deleted analysis for user two.
        """
        request = self._create_update_request(self.non_deleted_analysis_one_user_two)
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_one_user_two.analysis_id
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the other non deleted analysis did not get updated accidentally
        self.assertNotEqual(
            str(self.non_deleted_analysis_two_user_two.analysis_id),
            response.data["analysis_id"],
        )
        self.assertNotEqual(
            self.non_deleted_analysis_one_user_two.name, response.data["name"]
        )

    def _create_update_request(self, analysis):
        base_currency = (
            TypeCurrency.objects.all()
            .exclude(code=analysis.base_currency.code)
            .order_by("?")
            .first()
        )
        foreign_currency = (
            TypeCurrency.objects.all()
            .exclude(code=analysis.foreign_currency.code)
            .order_by("?")
            .first()
        )
        return {
            "name": analysis.name + " - edit",
            "category": TypeCategory.objects.all()
            .exclude(name=analysis.type_category.name)
            .order_by("?")
            .first()
            .name,
            "base_currency": {
                "code": base_currency.code,
                "country_name": base_currency.country_name,
            },
            "foreign_currency": {
                "code": foreign_currency.code,
                "country_name": foreign_currency.country_name,
            },
        }
