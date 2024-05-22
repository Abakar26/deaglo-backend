from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from api_gateway.utils.mixins import NonDeletedQuerySetMixin, DefaultPermissionsMixin
from authentication.models import User
from deaglo_admin.serializers import UserAdminSerializer


# TODO! We can add query params to filter user (Ex. level/role, org, delted, etc)
# TODO! Do we want to return the requesting user?
@method_decorator(swagger_auto_schema(tags=["Admin User"]), "get")
@method_decorator(swagger_auto_schema(tags=["Admin User"]), "post")
class UserListCreateApiView(
    DefaultPermissionsMixin,
    generics.ListCreateAPIView,
):
    """API view for retrieving list of user for admin user"""

    queryset = User.objects.filter()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]


@method_decorator(swagger_auto_schema(tags=["Admin User"]), "get")
@method_decorator(swagger_auto_schema(tags=["Admin User"]), "patch")
@method_decorator(swagger_auto_schema(tags=["Admin User"]), "put")
@method_decorator(swagger_auto_schema(tags=["Admin User"]), "delete")
class UserDetailUpdateDeleteApiView(
    DefaultPermissionsMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    """API view for retrieving detail of user for admin user"""

    queryset = User.objects.filter()
    serializer_class = UserAdminSerializer
    lookup_field = "user_id"
    permission_classes = [IsAdminUser]
