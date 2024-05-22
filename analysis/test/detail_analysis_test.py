from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from margin_simulation.factory import MarginSimulationFactory
from strategy_simulation.factory import StrategySimulationFactory
from hedge_simulation.factory import HedgeSimulationFactory


class DetailAnalysisTest(APITestCase):
    """
    Test case for handling get detail analysis in an API view.
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

    def test_retrieve_non_deleted_analysis_user_one(self):
        """
        Ensure we can retrieve non-deleted analysis for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.non_deleted_analysis_user_one.analysis_id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(self.non_deleted_analysis_user_one.analysis_id),
            response.data["analysis_id"],
        )

    def test_retrieve_deleted_analysis_user_one(self):
        """
        Ensure we can not retrieve deleted analysis for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.deleted_analysis_user_one.analysis_id},
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_forbidden_analysis_user_one(self):
        """
        Ensure we can not retrieve user two analysis for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_one_user_two.analysis_id
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_non_deleted_analysis_one_user_two(self):
        """
        Ensure we can retrieve correct non-deleted analysis for user two.
        """
        self.client.force_authenticate(user=self.user_two)

        response = self.client.get(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_one_user_two.analysis_id
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.name, response.data["name"]
        )
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.type_category.name,
            response.data["category"],
        )
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.base_currency.code,
            response.data["base_currency"]["code"],
        )
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.base_currency.country_name,
            response.data["base_currency"]["country_name"],
        )
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.foreign_currency.code,
            response.data["foreign_currency"]["code"],
        )
        self.assertEqual(
            self.non_deleted_analysis_one_user_two.foreign_currency.country_name,
            response.data["foreign_currency"]["country_name"],
        )
        self.assertNotEqual(
            str(self.non_deleted_analysis_two_user_two.analysis_id),
            response.data["analysis_id"],
        )

    def test_combined_simulations(self):
        for i in range(100):
            sim = StrategySimulationFactory(analysis=self.non_deleted_analysis_user_one)
            sim.save()
            margin = MarginSimulationFactory(
                analysis=self.non_deleted_analysis_user_one, strategy_simulation=sim
            )
            margin.save()
            hedge = HedgeSimulationFactory(analysis=self.non_deleted_analysis_user_one)
            hedge.save()

        self.client.force_authenticate(user=self.user_one)
        url = reverse(
            "simulation-list",
            kwargs={"analysis_id": self.non_deleted_analysis_user_one.analysis_id},
        )

        url += "?page=2"
        response = self.client.get(
            url,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
