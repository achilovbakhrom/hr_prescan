from django.urls import path

from apps.common.apis_admin import (
    AdminAnalyticsApi,
    AdminCompanyDetailApi,
    AdminCompanyListApi,
    AdminPlanDetailApi,
    AdminPlanManagementApi,
    AdminUserDetailApi,
    AdminUserListApi,
)

# Mounted at /api/admin/
admin_urlpatterns = [
    path("companies/", AdminCompanyListApi.as_view(), name="admin-company-list"),
    path("companies/<uuid:company_id>/", AdminCompanyDetailApi.as_view(), name="admin-company-detail"),
    path("users/", AdminUserListApi.as_view(), name="admin-user-list"),
    path("users/<uuid:user_id>/", AdminUserDetailApi.as_view(), name="admin-user-detail"),
    path("analytics/", AdminAnalyticsApi.as_view(), name="admin-analytics"),
    path("plans/", AdminPlanManagementApi.as_view(), name="admin-plan-management"),
    path("plans/<uuid:plan_id>/", AdminPlanDetailApi.as_view(), name="admin-plan-detail"),
]
