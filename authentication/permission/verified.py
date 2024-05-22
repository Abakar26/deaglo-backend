from rest_framework import permissions
from rest_framework.exceptions import APIException


class VerifiedPermission(permissions.BasePermission):
    """
    This permission class, `VerifiedPermission`, extends the DRF BasePermission class and
    restricts access to views based on the verification status of the requesting user.

    Methods:
        has_permission(request, view):
            Checks whether the requesting user is verified.

            Args:
                request (HttpRequest): The incoming HTTP request.
                view (APIView): The DRF view class.

            Returns:
                bool: True if the user is verified, raising an APIException with a 403 status
                      and an error message if the user is unverified.

            Example:
                To apply this permission to a DRF view, include it in the 'permission_classes'
                attribute of the view class.

                class MyVerifiedView(APIView):
                    permission_classes = [VerifiedPermission]
    """

    def has_permission(self, request, view):
        if request.user.is_verified:
            return True
        raise APIException(
            code=403, detail={"status": "error", "message": "Unverified User"}
        )
