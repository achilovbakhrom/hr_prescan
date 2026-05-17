from django.contrib import admin

from apps.applications.models import Application, ApplicationEvent, HiringManagerFeedback


class HiringManagerFeedbackInline(admin.TabularInline):
    model = HiringManagerFeedback
    extra = 0
    readonly_fields = ["id", "created_at", "updated_at"]


class ApplicationEventInline(admin.TabularInline):
    model = ApplicationEvent
    extra = 0
    readonly_fields = ["id", "created_at", "updated_at"]


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
    inlines = [HiringManagerFeedbackInline, ApplicationEventInline]


@admin.register(HiringManagerFeedback)
class HiringManagerFeedbackAdmin(admin.ModelAdmin):
    list_display = ["reviewer_name", "recommendation", "rating", "application", "created_at"]
    list_filter = ["recommendation", "rating"]
    search_fields = ["reviewer_name", "reviewer_role", "comment", "application__candidate_name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ApplicationEvent)
class ApplicationEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "actor_name", "application", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["actor_name", "message", "application__candidate_name"]
    readonly_fields = ["id", "created_at", "updated_at"]
