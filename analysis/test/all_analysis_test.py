from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategySimulationFactory
from margin_simulation.factory import MarginSimulationFactory
from hedge_simulation.factory import HedgeSimulationFactory


class AllAnalysisTest(APITestCase):
    """
    Test case for handling get all analysis in an API view.
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
        for i in range(30):
            sim = StrategySimulationFactory(analysis=self.non_deleted_analysis_user_one)
            sim.save()
            margin = MarginSimulationFactory(
                analysis=self.non_deleted_analysis_user_one, strategy_simulation=sim
            )
            margin.save()
            hedge = HedgeSimulationFactory(analysis=self.non_deleted_analysis_user_one)
            hedge.save()

    def test_retrieve_non_deleted_analysis_user_one(self):
        """
        Ensure we can retrieve non-deleted analyses for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse("analysis-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertNotIn(
            str(self.deleted_analysis_user_one.analysis_id),
            [a["analysis_id"] for a in response.data["results"]],
        )

    def test_retrieve_non_deleted_analysis_user_two(self):
        """
        Ensure we can retrieve non-deleted analyses for user two.
        """
        self.client.force_authenticate(user=self.user_two)

        response = self.client.get(
            reverse("analysis-list"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
