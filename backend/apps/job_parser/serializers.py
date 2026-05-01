from rest_framework import serializers

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services.normalization import normalize_employment


class ParsedVacancySourceOutputSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = ParsedVacancySource
        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "source_type",
            "url",
            "settings",
            "is_active",
            "last_synced_at",
            "sync_status",
            "sync_task_id",
            "sync_started_at",
            "sync_finished_at",
            "sync_error",
            "created_at",
            "updated_at",
        ]


class ParsedVacancySourceInputSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    source_type = serializers.ChoiceField(choices=ParsedVacancySource.Type.choices)
    url = serializers.URLField(required=False, allow_blank=True, default="")
    settings = serializers.DictField(required=False, default=dict)
    is_active = serializers.BooleanField(required=False, default=False)


class ParsedVacancyOutputSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    source_type = serializers.CharField(source="source.source_type", read_only=True)
    imported_vacancy_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = ParsedVacancy
        fields = [
            "id",
            "source",
            "source_name",
            "source_type",
            "external_id",
            "external_url",
            "title",
            "company_name",
            "description",
            "requirements",
            "responsibilities",
            "skills",
            "salary_min",
            "salary_max",
            "salary_currency",
            "location",
            "employment_type",
            "published_at",
            "expires_at",
            "last_seen_at",
            "status",
            "actuality_reason",
            "imported_vacancy_id",
            "created_at",
            "updated_at",
        ]


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


class TelegramMessageInputSerializer(serializers.Serializer):
    message_text = serializers.CharField()
    message_id = serializers.CharField(required=False, allow_blank=True, default="")
    message_url = serializers.URLField(required=False, allow_blank=True, default="")
    published_at = serializers.DateTimeField(required=False, allow_null=True)
