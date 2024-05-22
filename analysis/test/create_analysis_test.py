from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.models import Analysis
from authentication.factory import UserFactory


class CreateAnalysisTest(APITestCase):
    """
    Test case for handling create analysis in an API view.
    It is designed to test the behavior of an API view when an analysis that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating one verified user instance
        """
        self.user = UserFactory()
        self.analysis_data = {
            "name": "Test Analysis",
            "category": "Foreign investment",
            "base_currency": {
                "code": "USD",
                "country_name": "United States of America",
            },
            "foreign_currency": {"code": "EUR", "country_name": "European Union"},
        }

    def test_create_analysis(self):
        """
        Ensure we can create a new analysis and validate the data.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("analysis-list"), self.analysis_data, format="json"
        )

        # Check if the response is as expected
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.analysis_data["name"])
        self.assertEqual(response.data["category"], self.analysis_data["category"])
        self.assertEqual(
            response.data["base_currency"]["code"],
            self.analysis_data["base_currency"]["code"],
        )
        self.assertEqual(
            response.data["base_currency"]["country_name"],
            self.analysis_data["base_currency"]["country_name"],
        )
        self.assertEqual(
            response.data["foreign_currency"]["code"],
            self.analysis_data["foreign_currency"]["code"],
        )
        self.assertEqual(
            response.data["foreign_currency"]["country_name"],
            self.analysis_data["foreign_currency"]["country_name"],
        )

        # Fetch the newly created analysis from the database
        new_analysis = Analysis.objects.get(analysis_id=response.data["analysis_id"])

        # Validate the newly created analysis attributes
        self.assertFalse(new_analysis.is_deleted)
        self.assertEqual(new_analysis.name, self.analysis_data["name"])
        self.assertEqual(
            new_analysis.type_category.name, self.analysis_data["category"]
        )
        self.assertEqual(
            new_analysis.base_currency.code, self.analysis_data["base_currency"]["code"]
        )
        self.assertEqual(
            new_analysis.foreign_currency.code,
            self.analysis_data["foreign_currency"]["code"],
        )
        self.assertEqual(
            new_analysis.base_currency.country_name,
            self.analysis_data["base_currency"]["country_name"],
        )
        self.assertEqual(
            new_analysis.foreign_currency.country_name,
            self.analysis_data["foreign_currency"]["country_name"],
        )
