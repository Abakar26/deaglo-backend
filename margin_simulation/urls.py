from django.urls import path
from .views import *

urlpatterns = [
    # The idea here is to show all simulations for an admin
    # But for user, they need include the analysis which would route here and filter it further
    # path('', margin_simulation_list_view, name='margin-simulation-list'),
    # path('<uuid:margin_simulation_id>/', margin_simulation_detail_view, name='margin-simulation-detail'),
    # TODO: Might need to route from strategy simulation for create operations OR take from body like it is currently
    # TODO: routing the start sim id in the URL can make it easier to validate if it belongs to the user
    # We need to associate with an analysis in order to do create operations
    # So if the kwargs does not have analysis id, then error out
    # path('create/', margin_simulation_create_view, name='margin-simulation-create'),
    # path('<uuid:margin_simulation_id>/update/', margin_simulation_update_view, name='margin-simulation-update'),
    # path('<uuid:margin_simulation_id>/delete/', margin_simulation_destroy_view, name='margin-simulation-delete'),
]
