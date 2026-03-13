from django.urls import path

from apps.accounts.apis import (
    AcceptInvitationApi,
    CompanyProfileApi,
    CompanyRegisterApi,
    InviteHRApi,
    LoginApi,
    LogoutApi,
    MeApi,
    RegisterApi,
    TeamListApi,
    TeamMemberDetailApi,
    TokenRefreshApi,
    VerifyEmailApi,
)

# Auth URLs — mounted at /api/auth/
auth_urlpatterns = [
    path("register/", RegisterApi.as_view(), name="register"),
    path("login/", LoginApi.as_view(), name="login"),
    path("logout/", LogoutApi.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshApi.as_view(), name="token-refresh"),
    path("verify-email/", VerifyEmailApi.as_view(), name="verify-email"),
    path("me/", MeApi.as_view(), name="me"),
    path("company-register/", CompanyRegisterApi.as_view(), name="company-register"),
    path("accept-invitation/", AcceptInvitationApi.as_view(), name="accept-invitation"),
]

# HR URLs — mounted at /api/hr/company/
hr_urlpatterns = [
    path("profile/", CompanyProfileApi.as_view(), name="company-profile"),
    path("invite/", InviteHRApi.as_view(), name="invite-hr"),
    path("team/", TeamListApi.as_view(), name="team-list"),
    path("team/<uuid:user_id>/", TeamMemberDetailApi.as_view(), name="team-member-detail"),
]

# Keep backward compatibility — urlpatterns used by existing include("apps.accounts.urls")
urlpatterns = auth_urlpatterns
