from rest_framework import serializers

from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria


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
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class VacancyListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for vacancy lists."""

    criteria_count = serializers.IntegerField(read_only=True)
    questions_count = serializers.IntegerField(read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

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
            "criteria_count",
            "questions_count",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class VacancyDetailOutputSerializer(serializers.ModelSerializer):
    """Full vacancy detail with nested criteria and questions."""

    criteria = VacancyCriteriaOutputSerializer(many=True, read_only=True)
    questions = InterviewQuestionOutputSerializer(many=True, read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

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
            "interview_duration",
            "criteria",
            "questions",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PublicVacancyListOutputSerializer(serializers.ModelSerializer):
    """Public vacancy list — no salary or internal details."""

    company_name = serializers.CharField(source="company.name", read_only=True)

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
            "deadline",
            "created_at",
        ]
        read_only_fields = fields


class PublicVacancyDetailOutputSerializer(serializers.ModelSerializer):
    """Public vacancy detail — includes requirements but no salary or internal info."""

    company_name = serializers.CharField(source="company.name", read_only=True)

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
            "deadline",
            "interview_duration",
            "created_at",
        ]
        read_only_fields = fields
