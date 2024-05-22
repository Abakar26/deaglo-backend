from django.urls import path

from .views import *

urlpatterns = [
    # Fwd Efficiency
    path(
        "fwd-efficiency/",
        FwdEfficiencyListCreateAPIView.as_view(),
        name="fwd-efficiency-list",
    ),
    path(
        "fwd-efficiency/<uuid:fwd_efficiency_id>/",
        FwdEfficiencyRetrieveUpdateDestroyAPIView.as_view(),
        name="fwd-efficiency-detail",
    ),
    # Spot History
    path(
        "spot-history/",
        SpotHistoryListCreateAPIView.as_view(),
        # SpotHistoryDataView.as_view(),
        name="spot-history-list",
    ),
    path(
        "spot-history/<uuid:spot_history_id>/",
        SpotHistoryRetrieveUpdateDestroyAPIView.as_view(),
        name="spot-history-detail",
    ),
    # Fx Movement
    path(
        "fx-movement/",
        FxMovementListCreateAPIView.as_view(),
        name="fx-movement-list",
    ),
    path(
        "fx-movement/<uuid:fx_movement_id>/",
        FxMovementRetrieveUpdateDestroyAPIView.as_view(),
        name="fx-movement-detail",
    ),
    path(
        "",
        DefaultMarketView.as_view(),
        name="default-market",
    ),
    # Pricing
    path("pricing/spot", SpotRateView.as_view(), name="spot-rate"),
    path("pricing/forward", ForwardRateView.as_view(), name="forward-rate"),
    path("pricing/option", OptionPriceView.as_view(), name="option-price"),
]
