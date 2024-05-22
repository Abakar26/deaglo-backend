from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategySimulationFactory
from margin_simulation.factory import MarginSimulationFactory
from margin_simulation.models import MarginSimulation


class DeleteMarginSimulationTest(APITestCase):
    """
    Test case for handling deleting margin simulation in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted margin simulation that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create analysis instances
        3. Create strategy simulation instances
        4. Create margin simulation instances
        """
        # User
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        # Analysis
        self.analysis_one_user_one = AnalysisFactory(user=self.user_one)
        self.analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=True
        )
        self.analysis_two_user_two = AnalysisFactory(user=self.user_two)
        # Strategy Simulation
        self.strategy_simulation_one_analysis_one_user_one = StrategySimulationFactory(
            analysis=self.analysis_one_user_one
        )
        self.strategy_simulation_one_analysis_one_user_two = StrategySimulationFactory(
            analysis=self.analysis_one_user_two
        )
        self.strategy_simulation_one_analysis_two_user_two = StrategySimulationFactory(
            analysis=self.analysis_two_user_two,
            is_deleted=True,
        )
        self.strategy_simulation_two_analysis_two_user_two = StrategySimulationFactory(
            analysis=self.analysis_two_user_two
        )
        # Margin Simulation
        self.margin_simulation_one_analysis_one_user_one = MarginSimulationFactory(
            analysis=self.analysis_one_user_one,
            strategy_simulation=self.strategy_simulation_one_analysis_one_user_one,
        )
        self.margin_simulation_one_analysis_one_user_two = MarginSimulationFactory(
            analysis=self.analysis_one_user_two,
            strategy_simulation=self.strategy_simulation_one_analysis_one_user_two,
        )
        self.margin_simulation_one_analysis_two_user_two = MarginSimulationFactory(
            analysis=self.analysis_two_user_two,
            strategy_simulation=self.strategy_simulation_one_analysis_two_user_two,
        )
        self.margin_simulation_two_analysis_two_user_two = MarginSimulationFactory(
            analysis=self.analysis_two_user_two,
            strategy_simulation=self.strategy_simulation_two_analysis_two_user_two,
            is_deleted=True,
        )
        self.margin_simulation_three_analysis_two_user_two = MarginSimulationFactory(
            analysis=self.analysis_two_user_two,
            strategy_simulation=self.strategy_simulation_two_analysis_two_user_two,
        )

    def test_delete_margin_simulation_postive(self):
        """
        Test we can delete margin simulation that belongs to correct analysis and user
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify the db oject is now deleted
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_one_analysis_one_user_one.margin_simulation_id
        )
        self.assertTrue(db_object.is_deleted)

    def test_delete_margin_simulation_deleted_analysis(self):
        """
        Test we can not delete margin simulation that belongs to a deleted analysis
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_one_analysis_one_user_one.margin_simulation_id
        )
        self.assertEqual(
            self.margin_simulation_one_analysis_one_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_margin_simulation_deleted_strategy(self):
        """
        Test we can delete margin simulation with deleted strategy simulation
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_two_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify the db oject is same as before
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_one_analysis_two_user_two.margin_simulation_id
        )
        self.assertTrue(db_object.is_deleted)

    def test_delete_margin_simulation_deleted_simulation(self):
        """
        Test we can not delete margin simulation that was already deleted
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_two_analysis_two_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_two_analysis_two_user_two.margin_simulation_id
        )
        self.assertEqual(
            self.margin_simulation_two_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_margin_simulation_forbidden(self):
        """
        Test we can not delete margin simulation that belongs to another user
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_three_analysis_two_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_three_analysis_two_user_two.margin_simulation_id
        )
        self.assertEqual(
            self.margin_simulation_three_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_margin_simulation_mismatch_analysis(self):
        """
        Test we can not delete margin simulation with incorrect analysis input
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_three_analysis_two_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_three_analysis_two_user_two.margin_simulation_id
        )
        self.assertEqual(
            self.margin_simulation_three_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )
