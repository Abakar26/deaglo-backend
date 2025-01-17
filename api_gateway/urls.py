"""
URL configuration for api_gateway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from .views import Health, Currency

schema_view = get_schema_view(
    openapi.Info(
        title="Deaglo Documentation",
        default_version="v2",
        description="Django API documentation v2",
    ),
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    path("", Health.as_view()),
    path(
        "api/v2/",
        include(
            [
                path("admin/", include("deaglo_admin.urls")),
                path("auth/", include("authentication.urls")),
                path("analysis/", include("analysis.urls")),
                path("market/", include("market.urls")),
                path("currency/", Currency.as_view()),
                # TODO: maybe this can be removed, and it should be routing from the analysis app
                path("strategy-simulation/", include("strategy_simulation.urls")),
                path("margin-simulation/", include("margin_simulation.urls")),
                path("time-series/", include("time_series.urls")),
            ]
        ),
    ),
    re_path(
        r"^api/docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^api/redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
