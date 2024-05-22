from rest_framework.settings import api_settings


class DefaultPermissionsMixin:
    def get_permissions(self):
        # Get the default permissions
        default_permission_classes = [
            permission() for permission in api_settings.DEFAULT_PERMISSION_CLASSES
        ]
        # Get any custom permissions defined in the view
        custom_permission_classes = [
            permission() for permission in getattr(self, "permission_classes", [])
        ]
        # Combine and return them
        return default_permission_classes + custom_permission_classes
