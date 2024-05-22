from django.urls import path

from .views import *

urlpatterns = [
    # The idea here is to show all simulations for an admin
    # But for user, they need include the analysis which would route here and filter it further
    # path('', strategy_simulation_list_view, name='strategy-simulation-list'),
    # path('<uuid:strategy_simulation_id>/', strategy_simulation_detail_view, name='strategy-simulation-detail'),
    # We need to associate with an analysis in order to do create operations
    # So if the kwargs does not have analysis id, then error out
    # path('create/', strategy_simulation_create_view, name='strategy-simulation-create'),
    # path('<uuid:strategy_simulation_id>/update/', strategy_simulation_update_view, name='strategy-simulation-update'),
    # path('<uuid:strategy_simulation_id>/delete/', strategy_simulation_destroy_view, name='strategy-simulation-delete'),
    path("strategy/", StrategyListCreateAPIView.as_view(), name="strategy-list"),
    path(
        "strategy/<uuid:strategy_id>/",
        StrategyRetrieveUpdateDestroyAPIView.as_view(),
        name="strategy-detail",
    ),
]
