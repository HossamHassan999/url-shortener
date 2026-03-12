import logging
from rest_framework.views import exception_handler
from rest_framework import status
from config.responses import error_response

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Global exception handler to unify all API error responses
    and log exceptions for debugging.
    """

    # Log the exception with traceback
    logger.exception(exc)

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exceptions (500)
        return error_response(
            message="Internal server error",
            errors=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Handled exceptions (ValidationError, NotFound, etc.)
    # response.data is usually {"detail": "message"}
    errors = response.data

    # Wrap DRF exception into our unified error format
    return error_response(
        message="Request failed",
        errors=errors,
        status_code=response.status_code
    )
