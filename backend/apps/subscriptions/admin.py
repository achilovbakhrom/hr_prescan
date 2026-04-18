from django.contrib import admin

from apps.subscriptions.models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "price_monthly", "price_yearly", "is_active")
    list_filter = ("tier", "is_active")
    search_fields = ("name",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "billing_period", "is_active", "current_period_end")
    list_filter = ("billing_period", "is_active")
    search_fields = ("user__email",)
    raw_id_fields = ("user", "plan")
