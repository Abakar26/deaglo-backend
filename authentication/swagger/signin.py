from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status


def signin_swagger():
    """Swagger for Signin"""

    return swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["username", "password"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Authentication successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "verified": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
