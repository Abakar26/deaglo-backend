from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from authentication.factory import UserFactory
from strategy_simulation.factory import (
    StrategySimulationFactory,
    StrategyFactory,
    StrategyInstanceFactory,
)
from strategy_simulation.models import (
    StrategyLeg,
    StrategySimulation,
    StrategyInstance,
)


class DeleteStrategySimulationTest(APITestCase):
    """
    Test case for handling deleting strategy simulations in an API view.
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

    def test_delete_strategy_simulation_postive(self):
        """
        Test we can delete strategy simulation that belongs to correct analysis and user
        """
        custom_strategy = StrategyFactory(created_by_user=self.user_one)
        custom_strategy_legs = StrategyLeg.objects.filter(strategy=custom_strategy)
        for leg in custom_strategy_legs:
            StrategyInstanceFactory(
                strategy_simulation=self.strategy_simulation_one_analysis_one_user_one,
                strategy_leg=leg,
                instance_group=1,
            )
        strategy_instance = StrategyInstance.objects.filter(
            strategy_simulation=self.strategy_simulation_one_analysis_one_user_one
        )

        self.client.force_authenticate(self.user_one)
        response = self.client.delete(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_one.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify the db oject is now deleted
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        )
        self.assertTrue(db_object.is_deleted)
        # Verify that the strategy instances are soft deleted
        self.assertEqual(
            len(strategy_instance), db_object.strategy_instance.all().count()
        )
        self.assertEqual(len(db_object.strategy_instance.filter(is_deleted=False)), 0)

    def test_delete_strategy_simulation_deleted_analysis(self):
        """
        Test we can not delete strategy simulation that belongs to a deleted analysis
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
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
        # Verify the db oject is same as before
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_one_analysis_one_user_one.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_one_analysis_one_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_strategy_simulation_deleted_simulation(self):
        """
        Test we can not delete strategy simulation that was already deleted
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
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
        # Verify the db oject is same as before
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_two_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_two_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_strategy_simulation_forbidden(self):
        """
        Test we can not delete strategy simulation that belongs to another user
        """
        self.client.force_authenticate(self.user_one)
        response = self.client.delete(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_two_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )

    def test_delete_strategy_simulation_mismatch_analysis(self):
        """
        Test we can not delete strategy simulation belongs to correct user but incorrect analysis
        """
        self.client.force_authenticate(self.user_two)
        response = self.client.delete(
            reverse(
                "strategy-simulation-detail",
                kwargs={
                    "analysis_id": self.analysis_one_user_two.analysis_id,
                    "strategy_simulation_id": self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id,
                },
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify the db oject is same as before
        db_object = StrategySimulation.objects.get(
            pk=self.strategy_simulation_three_analysis_two_user_two.strategy_simulation_id
        )
        self.assertEqual(
            self.strategy_simulation_three_analysis_two_user_two.is_deleted,
            db_object.is_deleted,
        )
