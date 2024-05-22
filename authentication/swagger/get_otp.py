from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def get_otp_swagger():
    """
    Swagger for get OTP
    """
    return swagger_auto_schema(
        tags=["Authentication"],
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            503: openapi.Response(
                description="Service Unavailable",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
