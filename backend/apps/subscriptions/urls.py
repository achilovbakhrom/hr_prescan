from django.urls import path

from apps.subscriptions.apis import (
    CancelSubscriptionApi,
    PlanListApi,
    SubscriptionUsageApi,
    UserSubscriptionApi,
)

# Public — mounted at /api/subscriptions/
public_urlpatterns = [
    path("plans/", PlanListApi.as_view(), name="plan-list"),
]

# HR — mounted at /api/hr/subscription/
hr_urlpatterns = [
    path("", UserSubscriptionApi.as_view(), name="user-subscription"),
    path("cancel/", CancelSubscriptionApi.as_view(), name="cancel-subscription"),
    path("usage/", SubscriptionUsageApi.as_view(), name="subscription-usage"),
]
