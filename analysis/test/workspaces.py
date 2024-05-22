from django.urls import reverse
from rest_framework.test import APITestCase

from analysis.factory import AnalysisFactory, WorkspaceFactory
from authentication.factory import UserFactory


class WorkspaceTest(APITestCase):
    def setUp(self):
        """
        Set up the test environment by:
        1. Creating one verified user instance
        """
        self.user = UserFactory()
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_create_workspace(self):
        """
        Ensure we can create a workspace for user one.
        """

        data = {
            "name": "Test Workspace",
        }
        response = self.client.post(
            reverse("list-create-workspace"), data, format="json"
        )
        self.assertEqual(response.status_code, 201)

    def test_add_analysis_to_workspace(self):
        """
        Test case for adding an analysis to a workspace.

        This method creates an analysis and a workspace, then attempts to add the
        analysis to the workspace using the appropriate API endpoint. It verifies
        that the response status code is 204, indicating a successful addition.
        """
        analysis = AnalysisFactory(user=self.user)
        analysis.save()
        workspace = WorkspaceFactory(
            user=self.user, base_currency=analysis.base_currency
        )
        workspace.save()
        url = reverse(
            "add-remove-analysis-to-workspace",
            kwargs={
                "workspace_id": workspace.workspace_id,
                "analysis_id": analysis.analysis_id,
                "action": "add",
            },
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_delete_analysis_from_workspace(self):
        """
          Test deleting an analysis from a workspace via PATCH request.

        This method creates an analysis and a workspace using factories, associates the analysis
        with the workspace, sends a PATCH request to remove the analysis from the workspace,
        and verifies that the response status code is 204.

        """
        analysis = AnalysisFactory(user=self.user)
        analysis.save()
        workspace = WorkspaceFactory(user=self.user)
        workspace.analysis.add(analysis)
        workspace.save()
        url = reverse(
            "add-remove-analysis-to-workspace",
            kwargs={
                "workspace_id": workspace.workspace_id,
                "analysis_id": analysis.analysis_id,
                "action": "remove",
            },
        )
        response = self.client.patch(url)
        self.assertEqual(response.status_code, 204)

    def test_list_analysis_in_workspace(self):
        """
        Test listing analysis in workspaces via GET request.

        This method creates multiple workspaces with associated analyses using factories,
        sends a GET request to list the workspaces, and verifies that the response status code is 200.
        """
        for i in range(5):
            workspace = WorkspaceFactory(user=self.user)
            workspace.save()
            for j in range(5):
                analysis = AnalysisFactory(user=self.user)
                analysis.save()
                workspace.analysis.add(analysis)

        url = reverse("list-create-workspace")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_workspace(self):
        """
        Test retrieving a workspace via GET request.

        This method creates a workspace using a factory, sends a GET request to retrieve the workspace,
        and verifies that the response status code is 200."""
        workspace = WorkspaceFactory(user=self.user)
        workspace.save()
        url = reverse(
            "retrieve-update-workspace",
            kwargs={"workspace_id": workspace.workspace_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_workspace(self):
        """
        Test deleting a workspace via DELETE request.

        This method creates a workspace using a factory, sends a DELETE request to delete the workspace,
        and verifies that the response status code is 204.
        """
        workspace = WorkspaceFactory(user=self.user)
        workspace.save()
        url = reverse(
            "retrieve-update-workspace",
            kwargs={"workspace_id": workspace.workspace_id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_update_workspace(self):
        """
        Test updating a workspace via PATCH request.

        This method creates a workspace using a factory, constructs a PATCH request to update
        the workspace's details, and verifies that the response status code is 200.
        """
        workspace = WorkspaceFactory(user=self.user)
        workspace.save()
        url = reverse(
            "retrieve-update-workspace",
            kwargs={"workspace_id": workspace.workspace_id},
        )
        data = {"name": "Test Workspace"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, 200)
