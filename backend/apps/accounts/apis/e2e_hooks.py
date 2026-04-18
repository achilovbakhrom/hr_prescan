"""E2E test hooks — DEBUG/E2E-only endpoints for deterministic test setup.

These endpoints are gated behind `settings.ALLOW_E2E_HOOKS` and return 404
in environments where the flag is not enabled. They are used by the E2E
test suite to bypass real OAuth providers (Google, Telegram) and deterministically
put a user in a specific post-OAuth state.
"""

import uuid

from django.conf import settings
from django.http import Http404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserOutputSerializer


def _require_e2e_hooks_enabled() -> None:
    if not getattr(settings, "ALLOW_E2E_HOOKS", False):
        raise Http404()


class E2EOAuthSimulateApi(APIView):
    """POST /api/auth/debug/oauth-simulate/ — simulate a post-OAuth login.

    Returns JWT tokens + user for a user created to match one of three states:

    - `state=new_candidate`: brand-new social user, `onboarding_completed=False`.
      Frontend router should redirect this user to `/choose-role`.
    - `state=onboarded_candidate`: existing social user who finished onboarding
      as a candidate. Redirects to `/dashboard`.
    - `state=new_hr_needs_company`: social user who picked the HR role but has
      no company yet (`role=hr, company=null`). Redirects to `/company-setup`.

    Returns the same shape as `/api/auth/google/` so frontend flows are identical.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        state = serializers.ChoiceField(choices=["new_candidate", "onboarded_candidate", "new_hr_needs_company"])
        provider = serializers.ChoiceField(choices=["google", "telegram"], default="google")
        email = serializers.EmailField(required=False)

    def post(self, request: Request) -> Response:
        _require_e2e_hooks_enabled()

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data.get("email") or _generate_email(data["provider"])
        state = data["state"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": "E2E",
                "last_name": "OAuth",
                "role": User.Role.CANDIDATE,
                "email_verified": True,
            },
        )

        # Safety: never rewrite role/company/onboarding on an account we didn't
        # just create, unless it plainly belongs to the E2E test fleet. This
        # prevents the hook from hijacking real users if `ALLOW_E2E_HOOKS` is
        # ever accidentally enabled on a non-dev environment.
        if not created and not _is_test_account(user):
            return Response(
                {"detail": "Refusing to mutate an existing non-test account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if state == "new_candidate":
            user.role = User.Role.CANDIDATE
            user.company = None
            user.onboarding_completed = False
        elif state == "onboarded_candidate":
            user.role = User.Role.CANDIDATE
            user.company = None
            user.onboarding_completed = True
        elif state == "new_hr_needs_company":
            user.role = User.Role.HR
            user.company = None
            user.onboarding_completed = True

        user.save(update_fields=["role", "company", "onboarding_completed", "updated_at"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


_E2E_TEST_DOMAINS = ("e2e.test", "telegram.local", "prescreen-test.dev")


def _is_test_account(user: User) -> bool:
    """Heuristic: an account belongs to the E2E fleet if its email domain is
    on the known-test list. Used as a guard before the hook mutates a
    pre-existing user."""
    _, _, domain = user.email.rpartition("@")
    return domain.lower() in _E2E_TEST_DOMAINS


def _generate_email(provider: str) -> str:
    suffix = uuid.uuid4().hex[:10]
    if provider == "telegram":
        return f"tg_e2e_{suffix}@telegram.local"
    return f"e2e_oauth_{suffix}@e2e.test"
