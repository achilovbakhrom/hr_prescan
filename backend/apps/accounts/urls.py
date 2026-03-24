from django.urls import path

from apps.accounts.apis import (
    AcceptCompanyInvitationApi,
    AcceptInvitationApi,
    CompleteCompanySetupApi,
    CompleteOnboardingApi,
    CompanyProfileApi,
    CompanyRegisterApi,
    GoogleAuthApi,
    InviteHRApi,
    LoginApi,
    LogoutApi,
    MeApi,
    MyInvitationsApi,
    RegisterApi,
    TeamListApi,
    TeamMemberDetailApi,
    TelegramAuthApi,
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
    path("google/", GoogleAuthApi.as_view(), name="google-auth"),
    path("telegram/", TelegramAuthApi.as_view(), name="telegram-auth"),
    path("my-invitations/", MyInvitationsApi.as_view(), name="my-invitations"),
    path("accept-company-invitation/", AcceptCompanyInvitationApi.as_view(), name="accept-company-invitation"),
    path("complete-company-setup/", CompleteCompanySetupApi.as_view(), name="complete-company-setup"),
    path("complete-onboarding/", CompleteOnboardingApi.as_view(), name="complete-onboarding"),
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
