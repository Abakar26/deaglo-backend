from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from analysis.models import Analysis
from authentication.factory import UserFactory
from margin_simulation.factory import MarginSimulationFactory
from strategy_simulation.factory import StrategySimulationFactory


class DeleteAnalysisTest(APITestCase):
    """
    Test case for handling deleting analysis in an API view.
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
        3. Create margin simulation instances
        4. Create strategy simulation instances
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

        # Margin simulations and strategy simulations
        self.strategy_simulation_one_analysis_one_user_two = StrategySimulationFactory(
            analysis=self.non_deleted_analysis_one_user_two
        )
        self.strategy_simulation_one_analysis_two_user_two = StrategySimulationFactory(
            analysis=self.non_deleted_analysis_two_user_two
        )
        self.margin_simulation_one_analysus_two_user_two = MarginSimulationFactory(
            analysis=self.non_deleted_analysis_two_user_two,
            strategy_simulation=self.strategy_simulation_one_analysis_two_user_two,
        )

    def test_delete_non_deleted_analysis_user_one(self):
        """
        Ensure we can soft delete non-deleted analysis for user one via patch
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.delete(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.non_deleted_analysis_user_one.analysis_id},
            ),
            format="json",
        )

        # Ensure that the object in DB is soft deleted
        analysis = Analysis.objects.get(
            analysis_id=self.non_deleted_analysis_user_one.analysis_id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(analysis.is_deleted)
        self.assertFalse(self.non_deleted_analysis_user_one.is_deleted)  # Sanity check

    def test_delete_deleted_analysis_user_one(self):
        """
        Ensure we can not delete deleted analysis for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.delete(
            reverse(
                "analysis-detail",
                kwargs={"analysis_id": self.deleted_analysis_user_one.analysis_id},
            ),
            format="json",
        )

        # Ensure that the object in DB remains is_deleted
        analysis = Analysis.objects.get(
            analysis_id=self.deleted_analysis_user_one.analysis_id
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(analysis.is_deleted)
        self.assertTrue(self.deleted_analysis_user_one.is_deleted)

    def test_delete_forbidden_analysis_user_one(self):
        """
        Ensure we can not update user two analysis for user one.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.delete(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_one_user_two.analysis_id
                },
            ),
            format="json",
        )

        # Ensure that the object in DB remains is_deleted
        analysis = Analysis.objects.get(
            analysis_id=self.non_deleted_analysis_one_user_two.analysis_id
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(analysis.is_deleted)
        self.assertFalse(
            self.non_deleted_analysis_one_user_two.is_deleted
        )  # Sanity check

    def test_delete_non_deleted_analysis_one_user_two(self):
        """
        Ensure we can update correct non-deleted analysis for user two.
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.delete(
            reverse(
                "analysis-detail",
                kwargs={
                    "analysis_id": self.non_deleted_analysis_two_user_two.analysis_id
                },
            ),
            format="json",
        )

        # Ensure that the other non deleted analysis did not get deleted accidentally
        safe_analysis = Analysis.objects.get(
            analysis_id=self.non_deleted_analysis_one_user_two.analysis_id
        )
        deleted_analysis = Analysis.objects.get(
            analysis_id=self.non_deleted_analysis_two_user_two.analysis_id
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(safe_analysis.is_deleted)
        self.assertFalse(safe_analysis.strategy_simulation.first().is_deleted)
        self.assertTrue(deleted_analysis.strategy_simulation.first().is_deleted)
        self.assertTrue(deleted_analysis.margin_simulation.first().is_deleted)
