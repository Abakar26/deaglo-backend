from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from margin_simulation.models import MarginSimulation
from strategy_simulation.factory import StrategySimulationFactory


class CreateMarginSimulationTest(APITestCase):
    """
    Test case for handling creating margin simulation in an API view.
    It is designed to test the behavior of an API view when dealing with non deleted margin simulation that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Create analysis instances
        3. Create strategy simulation instances
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
        self.analysis_three_user_two = AnalysisFactory(user=self.user_two)
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
        self.strategy_simulation_one_analysis_three_user_two = (
            StrategySimulationFactory(analysis=self.analysis_three_user_two)
        )

        self.request = {
            "name": "Margin Simulation 1",
            "strategy_simulation_id": None,
            "status": "In Progress",
            "minimum_transfer_amount": 10000.00,
            "initial_margin_percentage": 0.55,
            "variation_margin_percentage": 0.67,
        }

    def test_create_margin_simulation_user_one_without_strategy_simulation(self):
        """
        Test we can not create margin simulation without strategy simulation id in request
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_margin_simulation_user_one(self):
        """
        Test we can create margin simulation for user one
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_one)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            self.request,
            format="json",
        )

        # Verify that the request and response match
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._test_margin_simulation_request_response(self.request, response.data)
        # Verify that the response and DB object are as expected
        db_object = MarginSimulation.objects.get(
            pk=response.data["margin_simulation_id"],
            analysis__pk=self.analysis_one_user_one.analysis_id,
        )
        self._test_margin_simulation_response(response.data, db_object)

    def test_create_margin_simulation_deleted_analysis(self):
        """
        Test we can not create margin simulation from deleted analysis
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_margin_simulation_deleted_strategy(self):
        """
        Test we can not create margin simulation with deleted strategy simulation
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_two_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_two_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_margin_simulation_forbidden_analysis(self):
        """
        Test we can not create margin simulation for an analysis belonging to another user
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_one_user_one.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_margin_simulation_forbidden_strategy_user(self):
        """
        Test we can not create margin simulation with strategy simulation that belongs to another user
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_two_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_margin_simulation_forbidden_strategy(self):
        """
        Test we can not create margin simulation with strategy simulation that belongs to another analysis for same user
        """
        self.request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.post(
            reverse(
                "margin-simulation-list",
                kwargs={"analysis_id": self.analysis_three_user_two.analysis_id},
            ),
            self.request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _test_margin_simulation_request_response(self, request, response):
        self.assertEqual(response["status"], request["status"])
        self.assertEqual(
            float(response["minimum_transfer_amount"]),
            float(request["minimum_transfer_amount"]),
        )
        self.assertEqual(
            response["initial_margin_percentage"], request["initial_margin_percentage"]
        )
        self.assertEqual(
            response["variation_margin_percentage"],
            request["variation_margin_percentage"],
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
