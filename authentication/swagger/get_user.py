from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def get_user_swagger():
    """
    Swagger for get user
    """
    return swagger_auto_schema(
        tags=["Authentication"],
        responses={
            200: openapi.Response(
                description="User details retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "username": openapi.Schema(type=openapi.TYPE_STRING),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "otherUserField": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
