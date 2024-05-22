from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from api_gateway.utils.mixins import NonDeletedQuerySetMixin, DefaultPermissionsMixin
from organization.models import Organization
from deaglo_admin.serializers import OrganizationSerializer


@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "get")
@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "post")
class OrganizationListCreateApiView(
    DefaultPermissionsMixin,
    generics.ListCreateAPIView,
):
    """API view for retrieving list of organization for admin user"""

    queryset = Organization.objects.filter()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]


@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "get")
@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "put")
@method_decorator(swagger_auto_schema(tags=["Admin Organization"]), "delete")
class OrganizationDetailUpdateDeleteApiView(
    DefaultPermissionsMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    """API view for retrieving detail of organization for admin user"""

    queryset = Organization.objects.filter()
    serializer_class = OrganizationSerializer
    lookup_field = "organization_id"
    permission_classes = [IsAdminUser]
