from rest_framework import serializers

from apps.applications.models import Application, HRCandidate
from apps.applications.serializer_utils import get_session_score
from apps.applications.serializers import ApplicationListOutputSerializer


class HRCandidateListOutputSerializer(serializers.ModelSerializer):
    application_count = serializers.SerializerMethodField()
    latest_application_id = serializers.SerializerMethodField()
    latest_vacancy_id = serializers.SerializerMethodField()
    latest_vacancy_title = serializers.SerializerMethodField()
    latest_company_name = serializers.SerializerMethodField()
    latest_status = serializers.SerializerMethodField()
    latest_match_score = serializers.SerializerMethodField()
    latest_prescanning_score = serializers.SerializerMethodField()
    latest_interview_score = serializers.SerializerMethodField()

    class Meta:
        model = HRCandidate
        fields = [
            "id",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "application_count",
            "latest_application_id",
            "latest_vacancy_id",
            "latest_vacancy_title",
            "latest_company_name",
            "latest_status",
            "latest_match_score",
            "latest_prescanning_score",
            "latest_interview_score",
            "first_seen_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def _applications(self, obj: HRCandidate):
        company_ids = self.context.get("company_ids", [])
        return Application.objects.filter(
            vacancy__company_id__in=company_ids,
            candidate_email__iexact=obj.candidate_email_normalized,
            is_deleted=False,
        ).select_related("vacancy", "vacancy__company")

    def _latest_visible_application(self, obj: HRCandidate) -> Application | None:
        return self._applications(obj).prefetch_related("sessions").order_by("-created_at").first()

    def get_application_count(self, obj: HRCandidate) -> int:
        return self._applications(obj).count()

    def get_latest_application_id(self, obj: HRCandidate) -> str | None:
        application = self._latest_visible_application(obj)
        return str(application.id) if application else None

    def get_latest_vacancy_id(self, obj: HRCandidate) -> str | None:
        application = self._latest_visible_application(obj)
        return str(application.vacancy_id) if application else None

    def get_latest_vacancy_title(self, obj: HRCandidate) -> str:
        application = self._latest_visible_application(obj)
        return application.vacancy.title if application else ""

    def get_latest_company_name(self, obj: HRCandidate) -> str:
        application = self._latest_visible_application(obj)
        return application.vacancy.company.name if application else ""

    def get_latest_status(self, obj: HRCandidate) -> str:
        application = self._latest_visible_application(obj)
        return application.status if application else ""

    def get_latest_match_score(self, obj: HRCandidate) -> str | None:
        application = self._latest_visible_application(obj)
        return str(application.match_score) if application and application.match_score is not None else None

    def get_latest_prescanning_score(self, obj: HRCandidate) -> float | None:
        application = self._latest_visible_application(obj)
        return get_session_score(application, "prescanning") if application else None

    def get_latest_interview_score(self, obj: HRCandidate) -> float | None:
        application = self._latest_visible_application(obj)
        return get_session_score(application, "interview") if application else None


class HRCandidateDetailOutputSerializer(HRCandidateListOutputSerializer):
    applications = serializers.SerializerMethodField()
    notes = serializers.CharField(read_only=True)

    class Meta(HRCandidateListOutputSerializer.Meta):
        fields = [*HRCandidateListOutputSerializer.Meta.fields, "notes", "applications"]

    def get_applications(self, obj: HRCandidate) -> list[dict]:
        applications = self._applications(obj).prefetch_related("sessions", "hiring_manager_feedback")
        return ApplicationListOutputSerializer(applications, many=True).data


class HRCandidateUpdateInputSerializer(serializers.Serializer):
    candidate_name = serializers.CharField(max_length=255, required=False)
    candidate_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
