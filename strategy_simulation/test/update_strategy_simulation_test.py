import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategySimulationFactory
from strategy_simulation.models import StrategySimulation


class UpdateStrategySimulationTest(APITestCase):
    """
    Test case for handling updating strategy simulations in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted strategy simulation that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create analysis instances
        """
        # Create users
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        # Create analysis
        self.analysis_one_user_one = AnalysisFactory(user=self.user_one)
        self.analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=True
        )
        self.analysis_two_user_two = AnalysisFactory(user=self.user_two)
        self.analysis_three_user_two = AnalysisFactory(user=self.user_two)
        # Create strategy simulations
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

        self.request = {
            "name": "Updated Strategy Simulation",
            "status": "In Progress",
            "simulation_environment": {
                "name": "Environment Test",
                "volatility": 0.076,
                "skew": 0,
                "appreciation_percent": 0.074,
            },
            "start_date": datetime.date(2023, 12, 15),
            "end_date": datetime.date(2024, 12, 15),
            "is_base_sold": True,
            "notional": 12345.67,
            "initial_spot_rate": 5.5,
            "initial_forward_rate": 4.3,
            "spread": 0.0,
            "strategy_instance": [
                {
                    "strategy_id": "5bd5fe24-079b-45a2-ab2b-17e717808bf7",
                    "is_custom": False,
                    "legs": [
                        {
                            "strategy_leg_id": "6beead00-4e23-44fa-8960-87cd4df1bb4c",
                            "premium_override": 0.1,
                            "leverage_override": 0.2,
                            "strike_override": 0.3,
                        }
                    ],
                }
            ],
        }

    def test_update_strategy_simulation_positive(self):
        """
        Test we can update the strategy simulation that belongs to user one
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )

        # Verify that the request and response match
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_simulation_environment_request_response(
            self.request["simulation_environment"],
            response.data["simulation_environment"],
        )
        self._test_strategy_simulation_request_response(self.request, response.data)
        self._test_strategy_instance_request_response(
            self.request["strategy_instance"], response.data["strategy_instance"]
        )

        # Verify that the response matches the updated DB object
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        )
        self._test_simulation_environment_response(
            response.data["simulation_environment"], db_object.simulation_environment
        )
        self._test_strategy_simulation_response(response.data, db_object)
        self._test_strategy_instance_response(
            response.data["strategy_instance"], db_object.strategy_instance
        )

    def test_update_strategy_simulation_deleted_analysis(self):
        """
        Test we can not update strategy simulation that belongs to a deleted analysis
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_two.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_one_analysis_one_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_one_analysis_one_user_two.initial_spot_rate,
            db_object.initial_spot_rate,
        )
        self.assertEqual(
            self.strategy_simulation_one_analysis_one_user_two.strategy_instance.all().count(),
            db_object.strategy_instance.all().count(),
        )

    def test_update_strategy_simulation_deleted_simulation(self):
        """
        Test we can not update deleted strategy simulation
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_two_analysis_two_user_two.initial_spot_rate,
            db_object.initial_spot_rate,
        )
        self.assertEqual(
            self.strategy_simulation_two_analysis_two_user_two.strategy_instance.all().count(),
            db_object.strategy_instance.all().count(),
        )

    def test_update_strategy_simulation_forbidden_analysis(self):
        """
        Test we can not update strategy simulation where analysis belong to another user
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.initial_spot_rate,
            db_object.initial_spot_rate,
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.strategy_instance.all().count(),
            db_object.strategy_instance.all().count(),
        )

    def test_update_strategy_simulation_forbidden_simulation(self):
        """
        Test we can not update strategy simulation that belongs to another user (using valid user analysis)
        Similar to mismatch
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.initial_spot_rate,
            db_object.initial_spot_rate,
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.strategy_instance.all().count(),
            db_object.strategy_instance.all().count(),
        )

    def test_update_strategy_simulation_mismatch(self):
        """
        Test we can not update strategy simulation that belongs to anothe analysis
        """
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_three_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.initial_spot_rate,
            db_object.initial_spot_rate,
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.strategy_instance.all().count(),
            db_object.strategy_instance.all().count(),
        )

    def _test_simulation_environment_request_response(self, request, response):
        self.assertEqual(response["name"], request["name"])
        self.assertEqual(response["volatility"], request["volatility"])
        self.assertEqual(response["skew"], request["skew"])
        self.assertEqual(
            response["appreciation_percent"], request["appreciation_percent"]
        )

    def _test_strategy_simulation_request_response(self, request, response):
        self.assertEqual(response["status"], request["status"])
        self.assertEqual(response["start_date"], request["start_date"])
        self.assertEqual(response["end_date"], request["end_date"])
        self.assertEqual(float(response["notional"]), float(request["notional"]))
        # self.assertEqual(response.data[0]["spot_rate_override"], request[""])
        # self.assertEqual(response.data[0]["forward_rate_override"], request[""])
        self.assertEqual(response["is_base_sold"], request["is_base_sold"])
        self.assertEqual(response["initial_spot_rate"], request["initial_spot_rate"])
        self.assertEqual(
            response["initial_forward_rate"], request["initial_forward_rate"]
        )

    def _test_strategy_instance_request_response(self, request, response):
        self.assertEqual(len(request), len(response))

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

    def _test_strategy_instance_response(self, response, instance):
        strategy_groups = instance.values("instance_group").distinct()
        self.assertEqual(len(response), len(strategy_groups))
