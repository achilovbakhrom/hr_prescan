from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.selectors_candidate_base import (
    get_hr_candidate_by_id,
    get_hr_candidates_filtered,
)
from apps.applications.serializers_candidate_base import (
    HRCandidateDetailOutputSerializer,
    HRCandidateListOutputSerializer,
    HRCandidateUpdateInputSerializer,
)
from apps.common.messages import MSG_NOT_IN_COMPANY


class HRCandidateBaseListApi(APIView):
    """GET /api/hr/candidate-base/ — deduplicated HR candidate base."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    class FilterSerializer(serializers.Serializer):
        search = serializers.CharField(required=False, allow_blank=True)
        ordering = serializers.ChoiceField(
            choices=[
                ("-last_activity_at", "Recently active"),
                ("last_activity_at", "Oldest activity"),
                ("candidate_name", "Name A-Z"),
                ("-candidate_name", "Name Z-A"),
            ],
            required=False,
            default="-last_activity_at",
        )

    def get(self, request: Request) -> Response:
        company_ids = get_user_live_company_ids(user=request.user)
        if not company_ids:
            return Response({"detail": str(MSG_NOT_IN_COMPANY)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        candidates = get_hr_candidates_filtered(
            user=request.user,
            search=serializer.validated_data.get("search") or None,
            ordering=serializer.validated_data.get("ordering", "-last_activity_at"),
        )
        return Response(
            HRCandidateListOutputSerializer(candidates, many=True, context={"company_ids": company_ids}).data,
            status=status.HTTP_200_OK,
        )


class HRCandidateBaseDetailApi(APIView):
    """GET/PATCH/DELETE /api/hr/candidate-base/{id}/."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def _get_candidate(self, request: Request, candidate_id: str):
        company_ids = get_user_live_company_ids(user=request.user)
        if not company_ids:
            return None, company_ids, Response({"detail": str(MSG_NOT_IN_COMPANY)}, status=status.HTTP_404_NOT_FOUND)
        candidate = get_hr_candidate_by_id(user=request.user, candidate_id=candidate_id)
        if candidate is None:
            return None, company_ids, Response({"detail": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)
        return candidate, company_ids, None

    def get(self, request: Request, candidate_id: str) -> Response:
        candidate, company_ids, error = self._get_candidate(request, candidate_id)
        if error is not None:
            return error
        return Response(
            HRCandidateDetailOutputSerializer(candidate, context={"company_ids": company_ids}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request, candidate_id: str) -> Response:
        candidate, company_ids, error = self._get_candidate(request, candidate_id)
        if error is not None:
            return error

        serializer = HRCandidateUpdateInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        fields = []
        for field, value in serializer.validated_data.items():
            setattr(candidate, field, value)
            fields.append(field)
        if fields:
            candidate.save(update_fields=[*fields, "updated_at"])
        return Response(
            HRCandidateDetailOutputSerializer(candidate, context={"company_ids": company_ids}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, candidate_id: str) -> Response:
        candidate, _company_ids, error = self._get_candidate(request, candidate_id)
        if error is not None:
            return error
        candidate.is_deleted = True
        candidate.save(update_fields=["is_deleted", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
