from __future__ import annotations

from uuid import UUID

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import get_or_create_candidate_profile
from apps.accounts.models import CandidateProfile, Company, CompanyMembership, User
from apps.accounts.serializers import UserOutputSerializer
from apps.accounts.services import create_user_company, switch_company, switch_to_personal
from apps.common.exceptions import ApplicationError


def _has_candidate_space(user: User) -> bool:
    return user.role == User.Role.CANDIDATE or CandidateProfile.objects.filter(user=user).exists()


def _has_hr_space(user: User) -> bool:
    return CompanyMembership.objects.filter(user=user, company__is_deleted=False).exists()


def _default_hr_membership(user: User, company_id: UUID | None = None) -> CompanyMembership | None:
    query = CompanyMembership.objects.filter(user=user, company__is_deleted=False).select_related("company")
    if company_id is not None:
        return query.filter(company_id=company_id).first()
    return query.order_by("-is_default", "created_at").first()


def _mode_payload(user: User) -> dict:
    has_candidate = _has_candidate_space(user)
    has_hr = _has_hr_space(user)
    available = []
    if has_hr:
        available.append(User.ActiveMode.HR)
    if has_candidate:
        available.append(User.ActiveMode.CANDIDATE)

    default_redirect = "/dashboard"
    if user.active_mode == User.ActiveMode.CANDIDATE:
        default_redirect = "/my-applications"

    return {
        "current_mode": user.active_mode,
        "available_modes": available,
        "can_create_hr_space": not has_hr,
        "can_create_candidate_space": not has_candidate,
        "default_redirect": default_redirect,
        "user": UserOutputSerializer(user).data,
    }


class AccountModesApi(APIView):
    """GET /api/auth/modes/ — return current mode and available spaces."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        request.user.refresh_from_db()
        return Response(_mode_payload(request.user), status=status.HTTP_200_OK)


class SwitchAccountModeApi(APIView):
    """POST /api/auth/modes/switch/ — switch between candidate and HR spaces."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        mode = serializers.ChoiceField(choices=User.ActiveMode.choices)
        company_id = serializers.UUIDField(required=False)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mode = serializer.validated_data["mode"]

        try:
            if mode == User.ActiveMode.CANDIDATE:
                if not _has_candidate_space(request.user):
                    raise ApplicationError("Create a candidate space before switching to candidate mode.")
                user = switch_to_personal(user=request.user)
            else:
                membership = _default_hr_membership(
                    request.user,
                    company_id=serializer.validated_data.get("company_id"),
                )
                if membership is None:
                    raise ApplicationError("Create an HR space before switching to HR mode.")
                user = switch_company(user=request.user, company_id=membership.company_id)
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_mode_payload(user), status=status.HTTP_200_OK)


class CreateHrSpaceApi(APIView):
    """POST /api/auth/modes/hr-space/ — create a company and enter HR mode."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255)
        size = serializers.ChoiceField(choices=Company.Size.choices)
        country = serializers.CharField(max_length=100)
        industries = serializers.ListField(child=serializers.SlugField(max_length=50), required=False, default=list)
        custom_industry = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        website = serializers.URLField(max_length=500, required=False, allow_blank=True, default="")
        description = serializers.CharField(required=False, allow_blank=True, default="")

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                if (
                    request.user.role == User.Role.CANDIDATE
                    and not CandidateProfile.objects.filter(user=request.user).exists()
                ):
                    get_or_create_candidate_profile(user=request.user)
                data = serializer.validated_data
                company = create_user_company(
                    user=request.user,
                    name=data["company_name"],
                    size=data["size"],
                    country=data["country"],
                    industries=data.get("industries", []),
                    custom_industry=data.get("custom_industry", ""),
                    website=data.get("website", ""),
                    description=data.get("description", ""),
                )
                user = switch_company(user=request.user, company_id=company.id)
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(_mode_payload(user), status=status.HTTP_201_CREATED)


class CreateCandidateSpaceApi(APIView):
    """POST /api/auth/modes/candidate-space/ — create profile data and enter candidate mode."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        first_name = serializers.CharField(max_length=150)
        last_name = serializers.CharField(max_length=150)
        phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")
        headline = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        location = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        with transaction.atomic():
            user = request.user
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.phone = data.get("phone", "")
            user.onboarding_completed = True
            user.save(update_fields=["first_name", "last_name", "phone", "onboarding_completed", "updated_at"])
            profile = get_or_create_candidate_profile(user=user)
            profile.headline = data.get("headline", "")
            profile.location = data.get("location", "")
            profile.save(update_fields=["headline", "location", "updated_at"])
            user = switch_to_personal(user=user)
        return Response(_mode_payload(user), status=status.HTTP_201_CREATED)
