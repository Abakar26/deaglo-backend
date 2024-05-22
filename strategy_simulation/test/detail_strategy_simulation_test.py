from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategySimulationFactory


class DetailStrategySimulationTest(APITestCase):
    """
    Test case for handling getting detail strategy simulation in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted strategy simulation that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create analysis instances
        3. Create strategy simulation instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        # User one analysis
        self.analysis_one_user_one = AnalysisFactory(user=self.user_one)
        self.analysis_two_user_one = AnalysisFactory(user=self.user_one)
        # User two analysis
        self.analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=True
        )
        self.analysis_two_user_two = AnalysisFactory(user=self.user_two)

        # User one strategy simulations
        self.strategy_simulation_one_analysis_one_user_one = StrategySimulationFactory(
            analysis=self.analysis_one_user_one
        )
        self.strategy_simulation_one_analysis_two_user_one = StrategySimulationFactory(
            analysis=self.analysis_two_user_one
        )
        # User two strategy simulations
        self.strategy_simulation_one_analysis_one_user_two = StrategySimulationFactory(
            analysis=self.analysis_one_user_two
        )
        self.strategy_simulation_two_analysis_two_user_two = StrategySimulationFactory(
            analysis=self.analysis_two_user_two, is_deleted=True
        )
        self.strategy_simulation_three_analysis_two_user_two = (
            StrategySimulationFactory(analysis=self.analysis_two_user_two)
        )

    def test_retrieve_strategy_simulation_user_one(self):
        """
        Test we can get startegy simulation belonging to an analysis and user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_simulation_environment_response(
            response.data["simulation_environment"],
            self.strategy_simulation_one_analysis_one_user_one.simulation_environment,
        )
        self._test_strategy_simulation_response(
            response.data, self.strategy_simulation_one_analysis_one_user_one
        )

    def test_retrieve_strategy_simulation_deleted_analysis(self):
        """
        Test we can not get startegy simulation belonging to a deleted analysis
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_two.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_strategy_simulation_deleted_simulation(self):
        """
        Test we can not get deleted startegy simulation belonging
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_strategy_simulation_forbidden_analysis(self):
        """
        Test we can not get strategy simulation that belongs to another user
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_strategy_simulation_mismatch_analysis(self):
        """
        Test we can not get strategy simulation for different analysis that belongs to same user
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.get(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_two_user_one.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _test_simulation_environment_response(self, response, instance):
        self.assertEqual(response["name"], instance.name)
        self.assertEqual(response["volatility"], instance.volatility)
        self.assertEqual(response["skew"], instance.skew)
        self.assertEqual(
            response["appreciation_percent"], instance.appreciation_percent
        )

    def _test_strategy_simulation_response(self, response, instance):
        self.assertEqual(response["status"], instance.type_status.name)
        self.assertEqual(response["start_date"], instance.start_date)
        self.assertEqual(response["end_date"], instance.end_date)
        self.assertEqual(response["notional"], instance.notional)
        # self.assertEqual(response.data[0]["spot_rate_override"], instance.spot_rate_override)
        # self.assertEqual(response.data[0]["forward_rate_override"], instance.forward_rate_override)
        self.assertEqual(response["is_base_sold"], instance.is_base_sold)
        self.assertEqual(response["initial_spot_rate"], instance.initial_spot_rate)
        self.assertEqual(
            response["initial_forward_rate"], instance.initial_forward_rate
        )
