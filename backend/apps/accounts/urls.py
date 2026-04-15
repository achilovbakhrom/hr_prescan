from django.urls import path

from apps.accounts.apis import (
    AcceptCompanyInvitationApi,
    CheckInvitationApi,
    AcceptInvitationApi,
    CandidateCVActivateApi,
    CandidateCVDetailApi,
    CandidateCVListCreateApi,
    CandidateLanguageDetailApi,
    CandidateLanguageListCreateApi,
    CandidateProfileApi,
    CandidateProfileSkillsApi,
    CertificationDetailApi,
    CertificationListCreateApi,
    CompleteCompanySetupApi,
    CompleteOnboardingApi,
    CompanyProfileApi,
    CvAiChatApi,
    CvAiGenerateApi,
    CvGeneratePdfApi,
    CvImproveSectionApi,
    CvParseApi,
    EducationDetailApi,
    EducationListCreateApi,
    GoogleAuthApi,
    InviteHRApi,
    LoginApi,
    LogoutApi,
    MeApi,
    MyCompaniesApi,
    MyInvitationsApi,
    ProfileCompletenessApi,
    RegisterApi,
    SwitchCompanyApi,
    SwitchToPersonalApi,
    TeamListApi,
    TeamMemberDetailApi,
    TelegramAuthApi,
    TokenRefreshApi,
    VerifyEmailApi,
    WorkExperienceDetailApi,
    WorkExperienceListCreateApi,
)

# Auth URLs — mounted at /api/auth/
auth_urlpatterns = [
    path("register/", RegisterApi.as_view(), name="register"),
    path("login/", LoginApi.as_view(), name="login"),
    path("logout/", LogoutApi.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshApi.as_view(), name="token-refresh"),
    path("verify-email/", VerifyEmailApi.as_view(), name="verify-email"),
    path("me/", MeApi.as_view(), name="me"),
    path("accept-invitation/", AcceptInvitationApi.as_view(), name="accept-invitation"),
    path("check-invitation/", CheckInvitationApi.as_view(), name="check-invitation"),
    path("google/", GoogleAuthApi.as_view(), name="google-auth"),
    path("telegram/", TelegramAuthApi.as_view(), name="telegram-auth"),
    path("my-invitations/", MyInvitationsApi.as_view(), name="my-invitations"),
    path("accept-company-invitation/", AcceptCompanyInvitationApi.as_view(), name="accept-company-invitation"),
    path("complete-company-setup/", CompleteCompanySetupApi.as_view(), name="complete-company-setup"),
    path("complete-onboarding/", CompleteOnboardingApi.as_view(), name="complete-onboarding"),
    path("my-companies/", MyCompaniesApi.as_view(), name="my-companies"),
    path("switch-company/", SwitchCompanyApi.as_view(), name="switch-company"),
    path("switch-personal/", SwitchToPersonalApi.as_view(), name="switch-personal"),
]

# HR URLs — mounted at /api/hr/company/
hr_urlpatterns = [
    path("profile/", CompanyProfileApi.as_view(), name="company-profile"),
    path("invite/", InviteHRApi.as_view(), name="invite-hr"),
    path("team/", TeamListApi.as_view(), name="team-list"),
    path("team/<uuid:user_id>/", TeamMemberDetailApi.as_view(), name="team-member-detail"),
]

# Candidate profile URLs — mounted at /api/candidate/profile/
candidate_profile_urlpatterns = [
    path("", CandidateProfileApi.as_view(), name="candidate-profile"),
    path("skills/", CandidateProfileSkillsApi.as_view(), name="candidate-profile-skills"),
    path("work-experiences/", WorkExperienceListCreateApi.as_view(), name="work-experience-list"),
    path("work-experiences/<uuid:pk>/", WorkExperienceDetailApi.as_view(), name="work-experience-detail"),
    path("educations/", EducationListCreateApi.as_view(), name="education-list"),
    path("educations/<uuid:pk>/", EducationDetailApi.as_view(), name="education-detail"),
    path("languages/", CandidateLanguageListCreateApi.as_view(), name="candidate-language-list"),
    path("languages/<uuid:pk>/", CandidateLanguageDetailApi.as_view(), name="candidate-language-detail"),
    path("certifications/", CertificationListCreateApi.as_view(), name="certification-list"),
    path("certifications/<uuid:pk>/", CertificationDetailApi.as_view(), name="certification-detail"),
    path("completeness/", ProfileCompletenessApi.as_view(), name="profile-completeness"),
    path("cvs/", CandidateCVListCreateApi.as_view(), name="candidate-cv-list"),
    path("cvs/<uuid:pk>/", CandidateCVDetailApi.as_view(), name="candidate-cv-detail"),
    path("cvs/<uuid:pk>/activate/", CandidateCVActivateApi.as_view(), name="candidate-cv-activate"),
    path("cv/generate-pdf/", CvGeneratePdfApi.as_view(), name="cv-generate-pdf"),
    path("cv/parse/", CvParseApi.as_view(), name="cv-parse"),
    path("cv/improve-section/", CvImproveSectionApi.as_view(), name="cv-improve-section"),
    path("cv/ai-chat/", CvAiChatApi.as_view(), name="cv-ai-chat"),
    path("cv/ai-generate/", CvAiGenerateApi.as_view(), name="cv-ai-generate"),
]

# Keep backward compatibility — urlpatterns used by existing include("apps.accounts.urls")
urlpatterns = auth_urlpatterns
