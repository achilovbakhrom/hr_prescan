from django.contrib import admin, messages

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services import start_source_sync, stop_source_sync


@admin.register(ParsedVacancySource)
class ParsedVacancySourceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "company",
        "source_type",
        "is_active",
        "sync_status",
        "last_synced_at",
        "created_at",
    ]
    list_filter = ["source_type", "is_active", "sync_status"]
    search_fields = ["name", "company__name", "url"]
    readonly_fields = [
        "id",
        "sync_status",
        "sync_task_id",
        "sync_started_at",
        "sync_finished_at",
        "sync_error",
        "created_at",
        "updated_at",
    ]
    actions = ["start_parsing", "stop_parsing"]

    @admin.action(description="Start parsing selected sources")
    def start_parsing(self, request, queryset):
        started = 0
        for source in queryset:
            try:
                start_source_sync(source=source)
            except Exception as exc:
                self.message_user(request, f"{source.name}: {exc}", level=messages.ERROR)
            else:
                started += 1
        if started:
            self.message_user(request, f"Started parsing for {started} source(s).", level=messages.SUCCESS)

    @admin.action(description="Stop parsing selected sources")
    def stop_parsing(self, request, queryset):
        stopped = 0
        for source in queryset:
            try:
                stop_source_sync(source=source)
            except Exception as exc:
                self.message_user(request, f"{source.name}: {exc}", level=messages.ERROR)
            else:
                stopped += 1
        if stopped:
            self.message_user(request, f"Stopped parsing for {stopped} source(s).", level=messages.SUCCESS)


@admin.register(ParsedVacancy)
class ParsedVacancyAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "status", "location", "last_seen_at", "imported_vacancy"]
    list_filter = ["status", "source__source_type"]
    search_fields = ["title", "company_name", "external_url"]
    readonly_fields = ["id", "fingerprint", "created_at", "updated_at"]
