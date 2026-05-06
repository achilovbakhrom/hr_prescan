from rest_framework import serializers

from apps.job_parser.models import ParsedVacancy
from apps.job_parser.services.contact_detection import parsed_vacancy_has_contact_info
from apps.job_parser.services.normalization import normalize_employment


class PublicParsedVacancyListOutputSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(read_only=True)
    company_logo = serializers.SerializerMethodField()
    is_remote = serializers.SerializerMethodField()
    employment_type = serializers.SerializerMethodField()
    experience_level = serializers.SerializerMethodField()
    cv_required = serializers.SerializerMethodField()
    deadline = serializers.DateTimeField(source="expires_at", allow_null=True, read_only=True)
    can_apply = serializers.SerializerMethodField()
    content_source = serializers.SerializerMethodField()
    has_contact_info = serializers.SerializerMethodField()

    class Meta:
        model = ParsedVacancy
        fields = [
            "id",
            "title",
            "description",
            "location",
            "is_remote",
            "employment_type",
            "experience_level",
            "company_name",
            "company_logo",
            "cv_required",
            "skills",
            "salary_min",
            "salary_max",
            "salary_currency",
            "deadline",
            "created_at",
            "can_apply",
            "content_source",
            "external_url",
            "has_contact_info",
        ]

    def get_company_logo(self, obj) -> None:
        return None

    def get_is_remote(self, obj) -> bool:
        return False

    def get_employment_type(self, obj) -> str:
        return normalize_employment(obj.employment_type)

    def get_experience_level(self, obj) -> str:
        return "middle"

    def get_cv_required(self, obj) -> bool:
        return False

    def get_can_apply(self, obj) -> bool:
        return False

    def get_content_source(self, obj) -> str:
        return "parsed"

    def get_has_contact_info(self, obj) -> bool:
        return parsed_vacancy_has_contact_info(obj)


class PublicParsedVacancyDetailOutputSerializer(PublicParsedVacancyListOutputSerializer):
    company = serializers.SerializerMethodField()
    responsibilities_translations = serializers.SerializerMethodField()
    requirements_translations = serializers.SerializerMethodField()
    description_translations = serializers.SerializerMethodField()
    title_translations = serializers.SerializerMethodField()
    interview_duration = serializers.SerializerMethodField()
    telegram_code = serializers.SerializerMethodField()

    class Meta(PublicParsedVacancyListOutputSerializer.Meta):
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
            "company",
            "company_name",
            "cv_required",
            "deadline",
            "interview_duration",
            "telegram_code",
            "title_translations",
            "description_translations",
            "requirements_translations",
            "responsibilities_translations",
            "created_at",
            "can_apply",
            "content_source",
            "external_url",
            "has_contact_info",
        ]

    def get_responsibilities_translations(self, obj) -> dict:
        return {}

    def get_requirements_translations(self, obj) -> dict:
        return {}

    def get_description_translations(self, obj) -> dict:
        return {}

    def get_title_translations(self, obj) -> dict:
        return {}

    def get_company(self, obj) -> None:
        return None

    def get_interview_duration(self, obj) -> int:
        return 0

    def get_telegram_code(self, obj) -> None:
        return None
