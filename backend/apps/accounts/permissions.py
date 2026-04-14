from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "admin"
        )


class IsHRManager(BasePermission):
    """Allow access only to HR manager users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "hr"
        )


class IsCandidate(BasePermission):
    """Allow access only to candidate users."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role == "candidate"
        )


class IsPlatformAdmin(BasePermission):
    """Allow access only to platform administrators (is_staff=True)."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsCompanyMember(BasePermission):
    """Check that the authenticated user belongs to the company referenced in the URL."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        company_id = view.kwargs.get("company_id")
        if company_id is None:
            return False

        return bool(
            hasattr(request.user, "company_id")
            and request.user.company_id is not None
            and str(request.user.company_id) == str(company_id)
        )
