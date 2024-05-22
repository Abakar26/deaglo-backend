from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from api_gateway.models import TypeStatus
from authentication.factory import UserFactory
from margin_simulation.factory import MarginSimulationFactory
from margin_simulation.models import MarginSimulation
from strategy_simulation.factory import StrategySimulationFactory


class UpdateMarginSimulationTest(APITestCase):
    """
    Test case for handling updating margin simulation in an API view.
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

    def test_update_margin_simulation_user_one_without_strategy_simulation(self):
        """
        Test we can not update margin simulation for user one without strategy simulation in request
        """
        request = self._update_request(self.margin_simulation_one_analysis_one_user_one)
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_margin_simulation_user_one(self):
        """
        Test we can update margin simulation for user one
        """
        request = self._update_request(self.margin_simulation_one_analysis_one_user_one)
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_one)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )

        # Verify that the request and response match
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_margin_simulation_request_response(request, response.data)
        # Verify that the response and DB object are as expected
        db_object = MarginSimulation.objects.get(
            pk=response.data["margin_simulation_id"],
            analysis__pk=self.analysis_one_user_one.analysis_id,
        )
        self._test_margin_simulation_response(response.data, db_object)

    def test_update_margin_simulation_deleted_analysis(self):
        """
        Test we can not update margin simulation from deleted analysis
        """
        request = self._update_request(self.margin_simulation_one_analysis_one_user_two)
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_two.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_margin_simulation_deleted_strategy(self):
        """
        Test we can update margin simulation that already contains deleted strategy simulation
        """
        request = self._update_request(self.margin_simulation_one_analysis_two_user_two)
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_two_user_two.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        # Verify that the db_object was updated
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_one_analysis_two_user_two.margin_simulation_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._test_margin_simulation_request_response(request, response.data)
        self._test_margin_simulation_response(response.data, db_object)

    def test_update_margin_simulation_input_deleted_strategy(self):
        """
        Test we can not update margin simulation to deleted startegy simulation
        """
        request = self._update_request(
            self.margin_simulation_three_analysis_two_user_two
        )
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_two_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_three_analysis_two_user_two.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        # Verify that the db oject was not updated
        db_object = MarginSimulation.objects.get(
            pk=self.margin_simulation_three_analysis_two_user_two.margin_simulation_id
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(
            request["strategy_simulation_id"],
            db_object.strategy_simulation.strategy_simulation_id,
        )
        self.assertFalse(db_object.strategy_simulation.is_deleted)
        # self.assertNotEqual(
        #     request["minimum_transfer_amount"], db_object.minimum_transfer_amount
        # )

    def test_update_margin_simulation_deleted_margin(self):
        """
        Test we can not update margin simulation that is already deleted
        """
        request = self._update_request(self.margin_simulation_two_analysis_two_user_two)
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_two_analysis_two_user_two.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_margin_simulation_forbidden_user(self):
        """
        Test we can not update margin simulation belonging to another user
        """
        request = self._update_request(self.margin_simulation_one_analysis_one_user_one)
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "margin_simulation_id": self.margin_simulation_one_analysis_one_user_one.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_margin_simulation_forbidden_strategy_user(self):
        """
        Test we can not update margin simulation to strategy simulation that belongs to another user
        """
        request = self._update_request(
            self.margin_simulation_three_analysis_two_user_two
        )
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_three_analysis_two_user_two.margin_simulation_id,
                },
            ),
            request,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_margin_simulation_forbidden_strategy_analysis(self):
        """
        Test we can not update margin simulation to strategy simulation that belongs to another analysis for same user
        """
        request = self._update_request(
            self.margin_simulation_three_analysis_two_user_two
        )
        request[
            "strategy_simulation_id"
        ] = self.strategy_simulation_one_analysis_three_user_two.strategy_simulation_id
        self.client.force_authenticate(user=self.user_two)
        response = self.client.put(
            reverse(
                "margin-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "margin_simulation_id": self.margin_simulation_three_analysis_two_user_two.margin_simulation_id,
                },
            ),
            request,
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
        self.assertEqual(
            response["strategy_simulation_id"],
            request["strategy_simulation_id"],
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

    def _update_request(self, instance):
        return {
            "name": "Updated Margin Simulation",
            "strategy_simulation_id": None,
            "status": TypeStatus.objects.exclude(name=instance.type_status.name)
            .order_by("?")
            .first()
            .name,
            "minimum_transfer_amount": instance.minimum_transfer_amount,
            "initial_margin_percentage": instance.initial_margin_percentage,
            "variation_margin_percentage": instance.variation_margin_percentage,
        }
