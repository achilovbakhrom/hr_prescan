from django.contrib import admin

from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore


class InterviewScoreInline(admin.TabularInline):
    model = InterviewScore
    extra = 0
    readonly_fields = ["id", "criteria", "score", "ai_notes"]


class InterviewIntegrityFlagInline(admin.TabularInline):
    model = InterviewIntegrityFlag
    extra = 0
    readonly_fields = ["id", "flag_type", "severity", "description", "timestamp_seconds"]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = [
        "application",
        "scheduled_at",
        "status",
        "overall_score",
        "created_at",
    ]
    list_filter = ["status"]
    search_fields = [
        "application__candidate_name",
        "application__candidate_email",
        "application__vacancy__title",
    ]
    readonly_fields = [
        "id",
        "livekit_room_name",
        "candidate_token",
        "recording_path",
        "transcript",
        "overall_score",
        "ai_summary",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["application"]
    inlines = [InterviewScoreInline, InterviewIntegrityFlagInline]


@admin.register(InterviewScore)
class InterviewScoreAdmin(admin.ModelAdmin):
    list_display = ["interview", "criteria", "score"]
    raw_id_fields = ["interview", "criteria"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InterviewIntegrityFlag)
class InterviewIntegrityFlagAdmin(admin.ModelAdmin):
    list_display = ["interview", "flag_type", "severity", "timestamp_seconds"]
    list_filter = ["flag_type", "severity"]
    raw_id_fields = ["interview"]
    readonly_fields = ["id", "created_at", "updated_at"]
