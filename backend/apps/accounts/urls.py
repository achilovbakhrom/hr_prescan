from django.urls import path

from apps.accounts.apis import (
    LoginApi,
    LogoutApi,
    MeApi,
    RegisterApi,
    TokenRefreshApi,
    VerifyEmailApi,
)

urlpatterns = [
    path("register/", RegisterApi.as_view(), name="register"),
    path("login/", LoginApi.as_view(), name="login"),
    path("logout/", LogoutApi.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshApi.as_view(), name="token-refresh"),
    path("verify-email/", VerifyEmailApi.as_view(), name="verify-email"),
    path("me/", MeApi.as_view(), name="me"),
]
