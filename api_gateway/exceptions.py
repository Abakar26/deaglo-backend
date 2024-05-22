import logging

from rest_framework import status
from rest_framework.exceptions import ValidationError as _ValidationError, APIException

logger = logging.getLogger()


def _snake_to_camel(snake_case_list):
    """
    Convert a list of snake_case strings to camelCase strings.
    """
    camel_case_list = []
    for snake_case_string in snake_case_list:
        words = snake_case_string.split("_")
        camel_case_string = words[0] + "".join(word.capitalize() for word in words[1:])
        camel_case_list.append(camel_case_string)
    return ", ".join(camel_case_list)


class GenericAPIError(APIException):
    """
    ValidationError(rest_framework.exceptions.ValidationError):
       Customized validation error class that formats the error response in a standard way.

       Args:
           error (str): A top-level error message.
           detail (dict): Error details.
           code (int): A custom error code.
    """

    default_detail = "A server error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, error, detail=None, code=None):
        logger.info(f"{detail} error {error}")
        self.default_detail = error
        if code != None:
            self.status_code = code
        super().__init__(detail, code=code)


class KeyMissingException(_ValidationError):
    """
    KeyMissingException(rest_framework.exceptions.ValidationError):
        Custom exception class for handling key missing errors.

        Args:
            e (Exception): The original exception containing information about the missing key.

        Example:
            KeyMissingException(e) would result in a validation error response like:
            {"status": "error", "message": "KeyMissingException missing"}
    """

    def __init__(self, e):
        super().__init__(f"{_snake_to_camel(e.args)} missing")
