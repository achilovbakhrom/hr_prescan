from rest_framework import serializers

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource


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
            "created_at",
            "updated_at",
        ]


class ParsedVacancySourceInputSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255)
    source_type = serializers.ChoiceField(choices=ParsedVacancySource.Type.choices)
    url = serializers.URLField(required=False, allow_blank=True, default="")
    settings = serializers.DictField(required=False, default=dict)
    is_active = serializers.BooleanField(required=False, default=True)


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


class TelegramMessageInputSerializer(serializers.Serializer):
    message_text = serializers.CharField()
    message_id = serializers.CharField(required=False, allow_blank=True, default="")
    message_url = serializers.URLField(required=False, allow_blank=True, default="")
    published_at = serializers.DateTimeField(required=False, allow_null=True)
