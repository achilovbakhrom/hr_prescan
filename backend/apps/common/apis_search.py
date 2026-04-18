"""Global HR search across vacancies and candidates."""

from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission
from apps.applications.models import Application
from apps.common.messages import MSG_NOT_IN_COMPANY
from apps.vacancies.models import Vacancy

RESULT_LIMIT = 10


class HRGlobalSearchApi(APIView):
    """GET /api/hr/search/?q=...

    Returns mixed results across vacancies and candidates for the company,
    capped at 10 hits per type. Used by the global Cmd-K search modal.
    """

    permission_classes = [HasHRPermission]

    class FilterSerializer(serializers.Serializer):
        q = serializers.CharField(required=False, allow_blank=True, default="")

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        q = filter_serializer.validated_data["q"].strip()

        if not q:
            return Response({"vacancies": [], "candidates": []}, status=status.HTTP_200_OK)

        vacancies = (
            Vacancy.objects.filter(company=company, is_deleted=False)
            .filter(Q(title__icontains=q) | Q(description__icontains=q))
            .order_by("-created_at")[:RESULT_LIMIT]
        )
        vacancy_results = [
            {
                "id": str(v.id),
                "title": v.title,
                "status": v.status,
            }
            for v in vacancies
        ]

        applications = (
            Application.objects.filter(vacancy__company=company, is_deleted=False)
            .filter(
                Q(candidate_name__icontains=q) | Q(candidate_email__icontains=q),
            )
            .select_related("vacancy")
            .order_by("-created_at")[:RESULT_LIMIT]
        )
        candidate_results = [
            {
                "id": str(a.id),
                "candidate_name": a.candidate_name,
                "candidate_email": a.candidate_email,
                "status": a.status,
                "vacancy_title": a.vacancy.title,
            }
            for a in applications
        ]

        return Response(
            {"vacancies": vacancy_results, "candidates": candidate_results},
            status=status.HTTP_200_OK,
        )
