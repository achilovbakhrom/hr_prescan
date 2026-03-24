from django.urls import path

from apps.integrations.apis import (
    TelegramAuthCheckApi,
    TelegramAuthRequestApi,
    TelegramLinkCodeApi,
    TelegramStatusApi,
    TelegramUnlinkApi,
    TelegramWebhookApi,
)

telegram_urlpatterns = [
    path("webhook/", TelegramWebhookApi.as_view(), name="telegram-webhook"),
    path("auth/request/", TelegramAuthRequestApi.as_view(), name="telegram-auth-request"),
    path("auth/check/<str:code>/", TelegramAuthCheckApi.as_view(), name="telegram-auth-check"),
]

hr_telegram_urlpatterns = [
    path("link-code/", TelegramLinkCodeApi.as_view(), name="telegram-link-code"),
    path("status/", TelegramStatusApi.as_view(), name="telegram-status"),
    path("unlink/", TelegramUnlinkApi.as_view(), name="telegram-unlink"),
]
