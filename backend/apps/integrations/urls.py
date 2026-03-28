from django.urls import path

from apps.integrations.apis import (
    TelegramLinkCodeApi,
    TelegramStatusApi,
    TelegramUnlinkApi,
    TelegramWebhookApi,
)

telegram_urlpatterns = [
    path("webhook/", TelegramWebhookApi.as_view(), name="telegram-webhook"),
]

hr_telegram_urlpatterns = [
    path("link-code/", TelegramLinkCodeApi.as_view(), name="telegram-link-code"),
    path("status/", TelegramStatusApi.as_view(), name="telegram-status"),
    path("unlink/", TelegramUnlinkApi.as_view(), name="telegram-unlink"),
]
