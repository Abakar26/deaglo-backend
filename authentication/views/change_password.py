from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_gateway.exceptions import KeyMissingException
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from authentication.swagger import change_password_swagger


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    """
    API view for changing a user's password.
    """

    @change_password_swagger()
    def patch(self, request):
        try:
            user = request.user
            old_password = request.data["old_password"]
            new_password = request.data["new_password"]
            confirm_password = request.data["confirm_password"]
        except KeyError as e:
            raise KeyMissingException(e)
        if not user.check_password(old_password):
            return Response(
                {"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST
            )
        validate_password(new_password, user=user)
        if new_password != confirm_password:
            return Response(
                {"error": "New password and confirm password do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response({"status": "success"})
