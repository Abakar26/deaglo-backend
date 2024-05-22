from django.urls import path

from analysis.views import *
from hedge_simulation.views import *
from margin_simulation.views import *
from strategy_simulation.views import *

urlpatterns = [
    # analysis
    path("", AnalysisListCreateAPIView.as_view(), name="analysis-list"),
    path("<uuid:analysis_id>/", AnalysisApiView.as_view(), name="analysis-detail"),
    path(
        "<uuid:analysis_id>/simulations",
        ListSimulationView.as_view(),
        name="simulation-list",
    ),
    # analysis workspaces
    path(
        "workspaces/",
        ListCreateWorkspaceAPIView.as_view(),
        name="list-create-workspace",
    ),
    path(
        "workspaces/<uuid:workspace_id>/",
        RetrieveUpdateDestroyWorkspaceAPIView.as_view(),
        name="retrieve-update-workspace",
    ),
    path(
        "workspaces/<uuid:workspace_id>/<uuid:analysis_id>/<str:action>/",
        AddRemoveAnalysisToWorkspace.as_view(),
        name="add-remove-analysis-to-workspace",
    ),
    # strategy simulation
    path(
        "<uuid:analysis_id>/strategy-simulation/",
        StrategySimulationListAPIView.as_view(),
        name="strategy-simulation-list",
    ),
    path(
        "<str:simulation_type>/<uuid:simulation_id>/pin",
        TogglePinnedSimulationView.as_view(),
        name="toggle-pin",
    ),
    path(
        "<uuid:analysis_id>/strategy-simulation/<uuid:strategy_simulation_id>/",
        StrategySimulationRetrieveUpdateDestroyAPIView.as_view(),
        name="strategy-simulation-detail",
    ),
    # margin simulation
    path(
        "<uuid:analysis_id>/margin-simulation/",
        MarginSimulationListCreateAPIView.as_view(),
        name="margin-simulation-list",
    ),
    path(
        "<uuid:analysis_id>/margin-simulation/<uuid:margin_simulation_id>/",
        MarginSimulationRetrieveUpdateDestroyAPIView.as_view(),
        name="margin-simulation-detail",
    ),
    # hedge IRR
    path(
        "<uuid:analysis_id>/hedge-simulation/",
        HedgeIRRListCreateView.as_view(),
        name="hedge-irr-list-create",
    ),
    path(
        "<uuid:analysis_id>/hedge-simulation/<uuid:hedge_simulation_id>",
        HedgeIRRRetrieveUpdateDestroyView.as_view(),
        name="hedge-irr-list-retrieve-update-destroy",
    ),
]
