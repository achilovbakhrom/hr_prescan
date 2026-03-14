from django.contrib import admin

from apps.subscriptions.models import CompanySubscription, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price_monthly", "price_yearly", "is_active")
    list_filter = ("tier", "is_active")
    search_fields = ("name",)


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("company", "plan", "billing_period", "is_active", "current_period_end")
    list_filter = ("billing_period", "is_active")
    search_fields = ("company__name",)
    raw_id_fields = ("company", "plan")
