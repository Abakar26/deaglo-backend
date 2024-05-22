import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import StrategyFactory
from strategy_simulation.models import (
    Strategy,
    StrategySimulation,
    StrategyInstance,
)


class CreateStrategySimulationTest(APITestCase):
    """
    Test case for handling creating strategy simulations in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted strategy simulation that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create analysis instances
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()
        self.analysis_one_user_one = AnalysisFactory(user=self.user_one)
        self.analysis_one_user_two = AnalysisFactory(
            user=self.user_two, is_deleted=True
        )
        self.analysis_two_user_two = AnalysisFactory(user=self.user_two)

        self.request = {
            "name": "Strategy Simulation 1",
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

    def test_create_strategy_simulation_user_one(self):
        """
        Test we can create a strategy simulation for user one
        """
        org_num_strategy_simulation = StrategySimulation.objects.all().count()
        org_num_strategy_instance = StrategyInstance.objects.all().count()
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            self.request,
            format="json",
        )

        # Verify that the request and response match
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._test_simulation_environment_request_response(
            self.request["simulation_environment"],
            response.data["simulation_environment"],
        )
        self._test_strategy_simulation_request_response(self.request, response.data)
        # Verify that the response and DB object are as expected
        db_object = StrategySimulation.objects.get(
            pk=response.data["strategy_simulation_id"],
            analysis__pk=self.analysis_one_user_one.analysis_id,
        )
        self._test_simulation_environment_response(
            response.data["simulation_environment"], db_object.simulation_environment
        )
        self._test_strategy_simulation_response(response.data, db_object)
        new_num_startegy_simulation = StrategySimulation.objects.all().count()
        new_num_strategy_instance = StrategyInstance.objects.all().count()
        self.assertNotEqual(org_num_strategy_simulation, new_num_startegy_simulation)
        self.assertNotEqual(org_num_strategy_instance, new_num_strategy_instance)

    def test_create_strategy_simulation_deleted_analysis(self):
        """
        Test we can not create a strategy simulation for a deleted analysis
        """
        org_num_strategy_simulation = StrategySimulation.objects.all().count()
        org_num_strategy_instance = StrategyInstance.objects.all().count()
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_num_startegy_simulation = StrategySimulation.objects.all().count()
        new_num_strategy_instance = StrategyInstance.objects.all().count()
        self.assertEqual(org_num_strategy_simulation, new_num_startegy_simulation)
        self.assertEqual(org_num_strategy_instance, new_num_strategy_instance)
        # self.assertEqual(response.data["message"], "")

    def test_create_strategy_simulation_forbidden_analysis(self):
        """
        Test we can not create a strategy simulation for an analysis belonging to another user
        """
        org_num_strategy_simulation = StrategySimulation.objects.all().count()
        org_num_strategy_instance = StrategyInstance.objects.all().count()
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_num_startegy_simulation = StrategySimulation.objects.all().count()
        new_num_strategy_instance = StrategyInstance.objects.all().count()
        self.assertEqual(org_num_strategy_simulation, new_num_startegy_simulation)
        self.assertEqual(org_num_strategy_instance, new_num_strategy_instance)

    def test_create_strategy_simulation_forbidden_custom_strategy(self):
        """
        Test we can not create a strategy simulation with a custom strategy that belongs to another user
        """
        org_num_strategy_simulation = StrategySimulation.objects.all().count()
        org_num_strategy_instance = StrategyInstance.objects.all().count()
        custom_strategy = StrategyFactory(created_by_user=self.user_one)
        custom_strategy = Strategy.objects.get(pk=custom_strategy.strategy_id)
        strategy_instance_legs = []
        for leg in custom_strategy.strategy_leg.all():
            strategy_instance_legs.append(
                {
                    "strategy_leg_id": str(leg.strategy_leg_id),
                    "premium_override": 0.1,
                    "leverage_override": 0.2,
                    "strike_override": 0.3,
                }
            )
        strategy_instance = []
        strategy_instance.append(
            {
                "strategy_id": str(custom_strategy.strategy_id),
                "is_custom": True,
                "legs": strategy_instance_legs,
            }
        )
        self.request["strategy_instance"] = strategy_instance
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "strategy-simulation-list",
                kwargs={"analysis_id": self.analysis_two_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        new_num_startegy_simulation = StrategySimulation.objects.all().count()
        new_num_strategy_instance = StrategyInstance.objects.all().count()
        self.assertEqual(org_num_strategy_simulation, new_num_startegy_simulation)
        self.assertEqual(org_num_strategy_instance, new_num_strategy_instance)

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
