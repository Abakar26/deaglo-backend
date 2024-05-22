from typing import Literal

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from analysis.models import Workspace, Analysis
from analysis.serializers import WorkspaceSerializer
from api_gateway.utils.mixins import NonDeletedQuerySetMixin
from authentication.mixins import UserQuerySetMixin
from api_gateway.exceptions import GenericAPIError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from typing import Literal


@method_decorator(swagger_auto_schema(tags=["Analysis"]), "get")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "post")
class ListCreateWorkspaceAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, ListCreateAPIView
):
    """
    API view to list and create workspaces.

    Inherits from ListCreateAPIView, NonDeletedQuerySetMixin, and UserQuerySetMixin.

    Attributes:
        queryset (QuerySet): The queryset of all workspaces.
        serializer_class (Serializer): The serializer class for workspace objects.
    """

    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer

    def perform_create(self, serializer):
        """
        Perform create action for a workspace.

        Args:
            serializer (Serializer): The serializer instance to create the workspace.
        """
        serializer.save(user=self.request.user)


@method_decorator(swagger_auto_schema(tags=["Analysis"]), "get")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "delete")
@method_decorator(swagger_auto_schema(tags=["Analysis"]), "put")
class RetrieveUpdateDestroyWorkspaceAPIView(
    NonDeletedQuerySetMixin, UserQuerySetMixin, RetrieveUpdateDestroyAPIView
):
    """
    API view to retrieve, update, and destroy a workspace.

    Inherits from RetrieveUpdateDestroyAPIView, NonDeletedQuerySetMixin, and UserQuerySetMixin.

    Attributes:
        queryset (QuerySet): The queryset of all workspaces.
        serializer_class (Serializer): The serializer class for workspace objects.
        lookup_field (UUID): The field to use for the lookup when retrieving a workspace.
    """

    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    lookup_field = "workspace_id"


@method_decorator(swagger_auto_schema(tags=["Analysis"]), "patch")
class AddRemoveAnalysisToWorkspace(APIView):
    """
    API view to add or remove an analysis to/from a workspace.

    Methods:
        patch(request, workspace_id, analysis_id, action): Handles PATCH requests.
    """

    def patch(
        self, request, workspace_id, analysis_id, action: Literal["add", "remove"]
    ):
        """
        Handle PATCH requests to add or remove an analysis to/from a workspace.

        Args:
            request: The HTTP request object.
            workspace_id (UUID): The ID of the workspace.
            analysis_id (UUID): The ID of the analysis.
            action (Literal["add", "remove"]): The action to perform (add or remove).

        Returns:
            Response: JSON response indicating the status of the operation.
        """
        workspace = get_object_or_404(Workspace, workspace_id=workspace_id)
        analysis = get_object_or_404(Analysis, analysis_id=analysis_id)
        # Adding a check for base currency
        if action == "add":
            if (
                workspace.base_currency
                and workspace.base_currency != analysis.base_currency
            ):
                raise GenericAPIError("Base currency mismatch", code=400)

            workspace.analysis.add(analysis)
        elif action == "remove":
            workspace.analysis.remove(analysis)
        return Response({"status": "success"}, status=204)
