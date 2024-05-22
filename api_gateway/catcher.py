import logging

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

from api_gateway.settings import DEBUG


# Custom error handler to override rest_framework builtin
def custom_exception_handler(exc, context):
    logger = logging.getLogger()
    logger.error(exc)
    set_rollback()
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    elif isinstance(exc, ValidationError):
        exc = exceptions.ValidationError(exc.messages)
    elif isinstance(exc, RuntimeError):
        exc = exceptions.APIException(exc.args[0])
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait
        if isinstance(exc.detail, list) and len(exc.detail) > 0:
            data = {"error": exc.detail[0]}
        elif isinstance(exc.detail, dict):
            detail = {}
            for key, value in exc.detail.items():
                if isinstance(value, list) and len(value) > 0:
                    detail[key] = value[0]
                elif isinstance(value, str):
                    detail[key] = value
            data = {"error": exc.default_detail, "detail": detail}
        else:
            data = {"error": exc.default_detail}
        return Response(data, status=exc.status_code, headers=headers)
    # Enable default error catching in debug mode
    return (
        None
        if DEBUG
        else Response({"error": "An internal error has occured"}, status=500)
    )
