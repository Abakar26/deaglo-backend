from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def verify_otp_swagger():
    """
    Verify OTP
    """
    return swagger_auto_schema(
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=["code"],
        ),
        responses={
            200: openapi.Response(
                description="OTP verification successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            404: openapi.Response(
                description="OTP not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
