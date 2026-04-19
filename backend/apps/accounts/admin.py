from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Company, CompanyMembership, Invitation, User


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "size", "country", "is_deleted", "created_at"]
    list_filter = ["size", "is_deleted"]
    search_fields = ["name", "country"]
    filter_horizontal = ["industries"]
    readonly_fields = ["id", "created_at", "updated_at", "deleted_at"]


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "company", "role", "is_default", "created_at"]
    list_filter = ["role", "is_default"]
    search_fields = ["user__email", "company__name"]
    raw_id_fields = ["user", "company"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "company", "is_accepted", "expires_at", "created_at"]
    list_filter = ["is_accepted"]
    search_fields = ["email", "company__name"]
    raw_id_fields = ["company", "invited_by"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "company",
        "subscription_status",
        "is_active",
        "email_verified",
    ]
    list_filter = ["role", "subscription_status", "is_active", "email_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        ("Role & Company", {"fields": ("role", "company")}),
        (
            "Subscription",
            {"fields": ("subscription_plan", "subscription_status", "trial_ends_at")},
        ),
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
