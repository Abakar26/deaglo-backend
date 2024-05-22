from django.urls import path
from .views import *

urlpatterns = [
    # Organization
    path(
        "organization/",
        OrganizationListCreateApiView.as_view(),
        name="admin-organization-list",
    ),
    path(
        "organization/<uuid:organization_id>/",
        OrganizationDetailUpdateDeleteApiView.as_view(),
        name="admin-organization-detail",
    ),
    # User
    path("user/", UserListCreateApiView.as_view(), name="admin-user-list"),
    path(
        "user/<uuid:user_id>/",
        UserDetailUpdateDeleteApiView.as_view(),
        name="admin-user-detail",
    ),
]
