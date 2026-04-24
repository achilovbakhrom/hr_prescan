from django.urls import path

from apps.integrations.apis import (
    HRTelegramLinkCodeApi,
    HRTelegramStatusApi,
    HRTelegramUnlinkApi,
    TelegramLinkCodeApi,
    TelegramStatusApi,
    TelegramUnlinkApi,
    TelegramWebhookApi,
)

telegram_urlpatterns = [
    path("link-code/", TelegramLinkCodeApi.as_view(), name="telegram-link-code"),
    path("status/", TelegramStatusApi.as_view(), name="telegram-status"),
    path("unlink/", TelegramUnlinkApi.as_view(), name="telegram-unlink"),
    path("<str:role>/webhook/", TelegramWebhookApi.as_view(), name="telegram-webhook"),
]

hr_telegram_urlpatterns = [
    path("link-code/", HRTelegramLinkCodeApi.as_view(), name="telegram-link-code"),
    path("status/", HRTelegramStatusApi.as_view(), name="telegram-status"),
    path("unlink/", HRTelegramUnlinkApi.as_view(), name="telegram-unlink"),
]
