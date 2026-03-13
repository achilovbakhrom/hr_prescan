from django.contrib import admin

from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria


class VacancyCriteriaInline(admin.TabularInline):
    model = VacancyCriteria
    extra = 0
    readonly_fields = ["id", "created_at", "updated_at"]


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "status", "visibility", "employment_type", "experience_level", "created_at"]
    list_filter = ["status", "visibility", "employment_type", "experience_level", "is_remote"]
    search_fields = ["title", "description", "company__name"]
    readonly_fields = ["id", "share_token", "created_at", "updated_at"]
    inlines = [VacancyCriteriaInline, InterviewQuestionInline]


@admin.register(VacancyCriteria)
class VacancyCriteriaAdmin(admin.ModelAdmin):
    list_display = ["name", "vacancy", "weight", "is_default", "order"]
    list_filter = ["is_default"]
    search_fields = ["name", "vacancy__title"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ["text_preview", "vacancy", "category", "source", "is_active", "order"]
    list_filter = ["source", "is_active"]
    search_fields = ["text", "vacancy__title"]
    readonly_fields = ["id", "created_at", "updated_at"]

    @admin.display(description="Text")
    def text_preview(self, obj: InterviewQuestion) -> str:
        return obj.text[:80] if len(obj.text) > 80 else obj.text
