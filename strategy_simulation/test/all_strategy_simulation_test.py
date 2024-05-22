from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategySimulationFactory


class AllStrategySimulationTest(APITestCase):
    """
    Test case for handling getting all strategy simulations in an API view.
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
        self.analysis_one_user_one = AnalysisFactory(user=self.user_one)
        self.analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=True
        )
        self.analysis_two_user_two = AnalysisFactory(user=self.user_two)

        self.strategy_simulation_one_analysis_one_user_one = StrategySimulationFactory(
            analysis=self.analysis_one_user_one
        )
        self.strategy_simulation_one_analysis_one_user_two = StrategySimulationFactory(
            analysis=self.analysis_one_user_two
        )
        self.strategy_simulation_two_analysis_two_user_two = StrategySimulationFactory(
            analysis=self.analysis_two_user_two, is_deleted=True
        )
        self.strategy_simulation_three_analysis_two_user_two = (
            StrategySimulationFactory(analysis=self.analysis_two_user_two)
        )

    def test_all_strategy_simulation_user_one(self):
        """
        Test we can get all startegy simulation belonging to an analysis and user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self._test_simulation_environment_response(
            response.data["results"][0]["simulation_environment"],
            self.strategy_simulation_one_analysis_one_user_one.simulation_environment,
        )
        self._test_strategy_simulation_response(
            response.data["results"][0],
            self.strategy_simulation_one_analysis_one_user_one,
        )

    def test_all_strategy_simulation_analysis_one_user_two(self):
        """
        Test we can not get all strategy simulation belonging to a deleted analysis
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_two.analysis_id},
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.data["message"], "Analysis not found")

    def test_all_strategy_simulation_analysis_two_user_two(self):
        """
        Test we can get all strategy simulations belonging to a non deleted analysis and user
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_two_user_two.analysis_id},
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self._test_simulation_environment_response(
            response.data["results"][0]["simulation_environment"],
            self.strategy_simulation_three_analysis_two_user_two.simulation_environment,
        )
        self._test_strategy_simulation_response(
            response.data["results"][0],
            self.strategy_simulation_three_analysis_two_user_two,
        )

    def test_all_forbidden_strategy_simulation_user_two(self):
        """
        Test we can not get strategy simulations for an analysis belonging to another user
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.get(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.data["message"], "Analysis not found")

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
