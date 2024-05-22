from django.urls import path

from .views import *

urlpatterns = [
    # Fwd Efficiency
    path(
        "spot-history/",
        SpotHistoryDataAPIView.as_view(),
        name="spot-history-data",
    ),
]
