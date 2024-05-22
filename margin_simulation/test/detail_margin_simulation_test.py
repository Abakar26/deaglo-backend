from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from margin_simulation.factory import MarginSimulationFactory
from margin_simulation.models import MarginSimulation
from strategy_simulation.factory import StrategySimulationFactory


class DetailMarginSimulationTest(APITestCase):
    """
    Test case for handling getting margin simulation in an API view.
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

    def test_retrieve_margin_simulation_user_one(self):
        """
        Test we can get startegy simulation belonging to an analysis and user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_margin_simulation_response(
            response.data, self.margin_simulation_one_analysis_one_user_one
        )

    def test_retrieve_margin_simulation_deleted_analysis(self):
        """
        Test we can not get margin simulation from deleted analysis
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
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

    def test_retrieve_margin_simulation_deleted_strategy(self):
        """
        Test we can get margin simulation with deleted strategy simulation
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_two_user_two.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_margin_simulation_response(
            response.data, self.margin_simulation_one_analysis_two_user_two
        )

    def test_retrieve_strategy_simulation_deleted_margin(self):
        """
        Test we can not get deleted margin simulation
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
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

    def test_retrieve_forbidden_margin_simulation_user_two(self):
        """
        Test we can not get margin simulation belonging to another user
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_margin_simulation_mismatch_analysis(self):
        """
        Test we can not get margin simulation with incorrect analysis input
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

    def _test_margin_simulation_response(self, response, instance):
        self.assertEqual(response["status"], instance.type_status.name)
        self.assertEqual(
            float(response["minimum_transfer_amount"]),
            float(instance.minimum_transfer_amount),
        )
        self.assertEqual(
            response["initial_margin_percentage"], instance.initial_margin_percentage
        )
        self.assertEqual(
            response["variation_margin_percentage"],
            instance.variation_margin_percentage,
        )
        self.assertEqual(
            response["strategy_simulation_id"],
            instance.strategy_simulation.strategy_simulation_id,
        )
        self.assertEqual(
            response["is_strategy_simulation_deleted"],
            instance.strategy_simulation.is_deleted,
        )
