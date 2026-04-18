from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


# ---------------------------------------------------------------------------
# HR granular permission constants
# ---------------------------------------------------------------------------
class HRPermissions:
    MANAGE_VACANCIES = "manage_vacancies"
    MANAGE_CANDIDATES = "manage_candidates"
    MANAGE_INTERVIEWS = "manage_interviews"
    MANAGE_TEAM = "manage_team"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SETTINGS = "manage_settings"

    ALL = [
        MANAGE_VACANCIES,
        MANAGE_CANDIDATES,
        MANAGE_INTERVIEWS,
        MANAGE_TEAM,
        VIEW_ANALYTICS,
        MANAGE_SETTINGS,
    ]


def user_has_hr_permission(user, permission: str) -> bool:
    """Check whether a user has a specific HR permission.

    Company admins (role='admin') always have all permissions.
    HR users must have the permission in their hr_permissions list.
    """
    if not user or not user.is_authenticated:
        return False
    if user.role == "admin":
        return True
    if user.role != "hr":
        return False
    return permission in (user.hr_permissions or [])


class HasHRPermission(BasePermission):
    """DRF permission that checks for a specific HR permission.

    Usage on a view:
        permission_classes = [HasHRPermission]
        hr_permission = HRPermissions.MANAGE_VACANCIES
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        required = getattr(view, "hr_permission", None)
        if required is None:
            # No specific permission required — just need to be admin or HR
            return request.user.role in ("admin", "hr")
        return user_has_hr_permission(request.user, required)


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
