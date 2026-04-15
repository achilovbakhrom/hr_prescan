from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Company, User


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "size", "country", "subscription_status", "created_at"]
    list_filter = ["size", "subscription_status"]
    search_fields = ["name", "country"]
    filter_horizontal = ["industries"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "company", "is_active", "email_verified"]
    list_filter = ["role", "is_active", "email_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        ("Role & Company", {"fields": ("role", "company")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "email_verified", "groups", "user_permissions")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "password1", "password2", "role")},
        ),
    )
