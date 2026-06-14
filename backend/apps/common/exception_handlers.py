from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.views import set_rollback

from apps.common.exceptions import ApplicationError


def application_exception_handler(exc, context):
    """DRF exception handler that maps business-logic errors to 400 responses.

    `ApplicationError` is a plain exception raised throughout the service layer.
    The default DRF handler does not recognize it, so it would surface as a 500.
    Here it is converted to a 400 with a consistent ``{"detail": ...}`` body,
    matching the manual try/except pattern used in the API views.
    """
    if isinstance(exc, ApplicationError):
        # ATOMIC_REQUESTS is enabled, so the request runs inside an atomic
        # block. Converting the exception to a Response stops it propagating,
        # which would otherwise commit any partial writes — mark for rollback,
        # exactly as DRF's default handler does for APIException. set_rollback()
        # safely no-ops when no atomic block is active.
        set_rollback()
        return Response(
            {"detail": exc.message, **({"extra": exc.extra} if exc.extra else {})},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return drf_exception_handler(exc, context)
