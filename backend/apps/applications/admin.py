from django.contrib import admin

from apps.applications.models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "candidate_name",
        "candidate_email",
        "vacancy",
        "status",
        "match_score",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = [
        "candidate_name",
        "candidate_email",
        "vacancy__title",
        "vacancy__company__name",
    ]
    readonly_fields = [
        "id",
        "cv_parsed_text",
        "cv_parsed_data",
        "match_score",
        "match_details",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["vacancy", "candidate"]
