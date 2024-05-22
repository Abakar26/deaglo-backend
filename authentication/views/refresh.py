from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


@method_decorator(swagger_auto_schema(tags=["Authentication"]), "post")
class TokenRefreshView(TokenRefreshView):
    """
    This view overrides the simple jwt TokenRefreshView
    """
