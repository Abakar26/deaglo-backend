from rest_framework.response import Response
from api_gateway.exceptions import GenericAPIError
from market.models import FwdEfficiency, FxMovement, SpotHistory
from market.serializers import (
    FwdEfficiencySerializer,
    FxMovementSerializer,
    SpotHistorySerializer,
)
from rest_framework.views import APIView


class DefaultMarketView(APIView):
    def get(self, request):
        user = request.user
        fx_movement_instance = FxMovement.objects.filter(
            user=user, is_default=True
        ).first()
        fwd_efficiency_instance = FwdEfficiency.objects.filter(
            user=user, is_default=True
        ).first()
        spot_history_instance = SpotHistory.objects.filter(
            user=user, is_default=True
        ).first()

        if fx_movement_instance and fwd_efficiency_instance and spot_history_instance:
            fx_movement = FxMovementSerializer(fx_movement_instance).data
            fwd_efficiency = FwdEfficiencySerializer(fwd_efficiency_instance).data
            spot_history = SpotHistorySerializer(spot_history_instance).data

            return Response(
                {
                    "fx_movement": fx_movement,
                    "fwd_efficiency": fwd_efficiency,
                    "spot_history": spot_history,
                }
            )
        else:
            raise GenericAPIError(f"Default market not found", code=404)
