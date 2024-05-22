from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory
from api_gateway.models import TypeStatus
from authentication.factory import UserFactory
from .factory import HedgeSimulationFactory
from .serializer import HedgeIRRSerializer


class HedgeSimulationTest(APITestCase):
    """
    Test cases for HedgeSimulation
    """

    def setUp(self):
        """
        Setup for HedgeSimulationTest

        """
        self.user = UserFactory()
        self.analysis = AnalysisFactory(user=self.user)
        self.user_deleted = UserFactory(is_deleted=True)
        self.analysis_deleted = AnalysisFactory(user=self.user, is_deleted=True)
        self.client.force_authenticate(user=self.user)
        self.hedge_simulation = HedgeSimulationFactory(analysis=self.analysis)
        self.hedge_simulation.simulation_environment.save()
        self.hedge_simulation.save()
        self.analysis.save()
        self.user.save()
        self.analysis_deleted.save()
        self.user_deleted.save()
        self.serialized_data = HedgeIRRSerializer(self.hedge_simulation).data
        self.harvest = [
            ("2015-10-01", -30600000),
            ("2016-01-01", -30600000),
            ("2016-04-01", -30600000),
            ("2016-07-01", -30600000),
            ("2017-01-04", -30600000),
            ("2017-07-01", -30600000),
            ("2018-01-03", -30600000),
            ("2018-10-03", 252146833),
            ("2019-01-01", 254900212),
            ("2019-04-01", 256650044),
            ("2019-07-01", 259619197),
            ("2019-10-01", 490666810),
            ("2020-01-01", 496359263),
            ("2020-04-01", 503832998),
            ("2020-07-01", 516602988),
        ]

    def test_create_hedge(self):
        """
        Test create hedge
        """
        url = reverse(
            "hedge-irr-list-create", kwargs={"analysis_id": self.analysis.analysis_id}
        )

        payload = {
            "harvest": self.harvest,
            "name": self.serialized_data["name"],
            "simulation_environment": self.serialized_data["simulation_environment"],
            "fwd_rates": self.serialized_data["fwd_rates"],
        }
        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_hedge(self):
        """
        Test delete hedge
        """
        url = reverse(
            "hedge-irr-list-retrieve-update-destroy",
            kwargs={
                "analysis_id": self.hedge_simulation.analysis.pk,
                "hedge_simulation_id": self.hedge_simulation.pk,
            },
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_hedge(self):
        """
        Test update hedge
        """
        url = reverse(
            "hedge-irr-list-retrieve-update-destroy",
            kwargs={
                "analysis_id": self.hedge_simulation.analysis.pk,
                "hedge_simulation_id": self.hedge_simulation.pk,
            },
        )
        data = {
            "harvest": self.harvest,
            "name": "updated name",
            "fwd_rates": self.hedge_simulation.fwd_rates,
            "simulation_environment": self.serialized_data["simulation_environment"],
            "status": self.hedge_simulation.status.name,
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        del data["harvest"]
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "send post request without harvest data",
        )

    def test_get_hedge(self):
        """
        Test get hedge
        """
        url = reverse(
            "hedge-irr-list-retrieve-update-destroy",
            kwargs={
                "analysis_id": self.hedge_simulation.analysis.pk,
                "hedge_simulation_id": self.hedge_simulation.pk,
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partial_update_hedge(self):
        """
        Test partial update hedge
        """
        url = reverse(
            "hedge-irr-list-retrieve-update-destroy",
            kwargs={
                "analysis_id": self.hedge_simulation.analysis.pk,
                "hedge_simulation_id": self.hedge_simulation.pk,
            },
        )
        data = {
            "name": "updated name",
        }
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "simulation_environment": self.serialized_data["simulation_environment"],
            "status": TypeStatus.objects.get(
                pk="6f3d8caa-ca80-4117-8d03-c487c43338bc"
            ).name,
        }
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
