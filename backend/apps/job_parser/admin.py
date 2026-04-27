from django.contrib import admin

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource


@admin.register(ParsedVacancySource)
class ParsedVacancySourceAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "source_type", "is_active", "last_synced_at", "created_at"]
    list_filter = ["source_type", "is_active"]
    search_fields = ["name", "company__name", "url"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ParsedVacancy)
class ParsedVacancyAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "status", "location", "last_seen_at", "imported_vacancy"]
    list_filter = ["status", "source__source_type"]
    search_fields = ["title", "company_name", "external_url"]
    readonly_fields = ["id", "fingerprint", "created_at", "updated_at"]
