from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status


def change_password_swagger():
    """Swagger for change Password"""
    return swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "oldPassword": openapi.Schema(type=openapi.TYPE_STRING),
                "newPassword": openapi.Schema(type=openapi.TYPE_STRING),
                "confirmPassword": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["oldPassword", "newPassword", "confirmPassword"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad request or validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
