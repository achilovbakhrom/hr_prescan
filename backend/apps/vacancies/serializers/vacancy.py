from rest_framework import serializers

from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria
from apps.vacancies.serializers.employer import EmployerCompanyOutputSerializer


class VacancyCriteriaOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyCriteria
        fields = [
            "id",
            "name",
            "description",
            "weight",
            "is_default",
            "order",
            "step",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class InterviewQuestionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = [
            "id",
            "text",
            "category",
            "source",
            "order",
            "is_active",
            "step",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class VacancyListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for vacancy lists."""

    criteria_count = serializers.IntegerField(read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    candidates_total = serializers.IntegerField(read_only=True, default=0)
    candidates_interviewed = serializers.IntegerField(read_only=True, default=0)
    candidates_shortlisted = serializers.IntegerField(read_only=True, default=0)
    candidates_rejected = serializers.IntegerField(read_only=True, default=0)
    candidates_hired = serializers.IntegerField(read_only=True, default=0)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    employer_name = serializers.CharField(source="employer.name", read_only=True, default=None, allow_null=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "status",
            "visibility",
            "location",
            "is_remote",
            "employment_type",
            "experience_level",
            "deadline",
            "interview_mode",
            "interview_enabled",
            "cv_required",
            "prescanning_language",
            "criteria_count",
            "questions_count",
            "candidates_total",
            "candidates_interviewed",
            "candidates_shortlisted",
            "candidates_rejected",
            "candidates_hired",
            "created_by_email",
            "employer_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class VacancyDetailOutputSerializer(serializers.ModelSerializer):
    """Full vacancy detail with nested criteria and questions."""

    criteria = VacancyCriteriaOutputSerializer(many=True, read_only=True)
    questions = InterviewQuestionOutputSerializer(many=True, read_only=True)
    employer = EmployerCompanyOutputSerializer(read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)
    candidates_total = serializers.SerializerMethodField()
    candidates_shortlisted = serializers.SerializerMethodField()

    def get_candidates_total(self, obj) -> int:
        return obj.applications.filter(is_deleted=False).count()

    def get_candidates_shortlisted(self, obj) -> int:
        return obj.applications.filter(is_deleted=False, status="shortlisted").count()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "skills",
            "salary_min",
            "salary_max",
            "salary_currency",
            "location",
            "is_remote",
            "employment_type",
            "experience_level",
            "deadline",
            "status",
            "visibility",
            "share_token",
            "interview_mode",
            "interview_enabled",
            "cv_required",
            "interview_duration",
            "company_info",
            "prescanning_prompt",
            "interview_prompt",
            "prescanning_language",
            "keywords",
            "employer",
            "criteria",
            "questions",
            "candidates_total",
            "candidates_shortlisted",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PublicVacancyListOutputSerializer(serializers.ModelSerializer):
    """Public vacancy list -- includes salary and skills for job seekers."""

    company_name = serializers.CharField(source="company.name", read_only=True)
    employer_name = serializers.CharField(source="employer.name", read_only=True, default=None, allow_null=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "description",
            "location",
            "is_remote",
            "employment_type",
            "experience_level",
            "company_name",
            "employer_name",
            "cv_required",
            "skills",
            "salary_min",
            "salary_max",
            "salary_currency",
            "deadline",
            "created_at",
        ]
        read_only_fields = fields


class PublicVacancyDetailOutputSerializer(serializers.ModelSerializer):
    """Public vacancy detail -- includes requirements but no salary or internal info."""

    company_name = serializers.CharField(source="company.name", read_only=True)
    employer = EmployerCompanyOutputSerializer(read_only=True)

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "skills",
            "location",
            "is_remote",
            "employment_type",
            "experience_level",
            "company_name",
            "employer",
            "cv_required",
            "deadline",
            "interview_duration",
            "created_at",
        ]
        read_only_fields = fields
