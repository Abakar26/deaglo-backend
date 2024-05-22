from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api_gateway.models import TypeCurrency
from authentication.factory import UserFactory
from market.factory import FwdEfficiencyFactory
from market.models import FwdEfficiency


class UpdateFwdEfficiencyTest(APITestCase):
    """
    Test case for handling updating fwd efficiency in an API view.
    It is designed to test the behavior of an API view when dealing with fwd efficiency that belong to the user
    """

    def setUp(self):
        """
        Set up the test environment by:
        1. Creating two verified user instances
        2. Creating fwd efficiency instances where:
           - One saved belongs to user one
           - One not saved belong to user two
        """
        self.user_one = UserFactory()
        self.user_two = UserFactory()

        self.fwd_efficiency_one_user_one = FwdEfficiencyFactory(
            user=self.user_one, is_deleted=False
        )
        self.fwd_efficiency_one_user_two = FwdEfficiencyFactory(
            user=self.user_two, is_deleted=True
        )

    def test_update_not_saved_fwd_efficiency_user_two(self):
        """
        Test we can update non saved fwd efficiency for user two
        """
        request = self._update_request(self.fwd_efficiency_one_user_two)
        self.client.force_authenticate(self.user_two)
        response = self.client.put(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_two.fwd_efficiency_id
                },
            ),
            request,
            format="json",
        )

        # Verify that the request and response are as expected
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(self.fwd_efficiency_one_user_two.fwd_efficiency_id),
            response.data["fwd_efficiency_id"],
        )
        self.assertEqual(request["name"], response.data["name"])
        self.assertEqual(
            request["base_currency"]["code"], response.data["base_currency"]["code"]
        )
        self.assertEqual(
            request["base_currency"]["country_name"],
            response.data["base_currency"]["country_name"],
        )
        self.assertEqual(
            request["foreign_currency"]["code"],
            response.data["foreign_currency"]["code"],
        )
        self.assertEqual(
            request["foreign_currency"]["country_name"],
            response.data["foreign_currency"]["country_name"],
        )
        self.assertEqual(request["duration_months"], response.data["duration_months"])

        # Verify that the db object was updated as expected
        db_object = FwdEfficiency.objects.get(pk=response.data["fwd_efficiency_id"])
        self.assertEqual(request["name"], db_object.name)
        self.assertEqual(request["base_currency"]["code"], db_object.base_currency.code)
        self.assertEqual(
            request["base_currency"]["country_name"],
            db_object.base_currency.country_name,
        )
        self.assertEqual(
            request["foreign_currency"]["code"], db_object.foreign_currency.code
        )
        self.assertEqual(
            request["foreign_currency"]["country_name"],
            db_object.foreign_currency.country_name,
        )
        self.assertEqual(request["duration_months"], db_object.duration)

    def test_update_forbidden_fwd_efficiency_user_two(self):
        """
        Test we can not update fwd efficiency belonging to another user
        """
        request = self._update_request(self.fwd_efficiency_one_user_one)
        self.client.force_authenticate(self.user_two)
        response = self.client.put(
            reverse(
                "fwd-efficiency-detail",
                kwargs={
                    "fwd_efficiency_id": self.fwd_efficiency_one_user_one.fwd_efficiency_id
                },
            ),
            request,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _update_request(self, fwd_efficiency):
        updated_base_currency = (
            TypeCurrency.objects.all()
            .exclude(code=fwd_efficiency.base_currency.code)
            .order_by("?")
            .first()
        )
        updated_foreign_currency = (
            TypeCurrency.objects.all()
            .exclude(code=fwd_efficiency.foreign_currency.code)
            .order_by("?")
            .first()
        )

        return {
            "name": fwd_efficiency.name + " - edit",
            "base_currency": {
                "code": updated_base_currency.code,
                "country_name": updated_base_currency.country_name,
            },
            "foreign_currency": {
                "code": updated_foreign_currency.code,
                "country_name": updated_foreign_currency.country_name,
            },
            "duration_months": fwd_efficiency.duration + 1,
        }
