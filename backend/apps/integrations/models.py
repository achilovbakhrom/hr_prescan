import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class TelegramLinkCode(BaseModel):
    """One-time token for linking a Telegram account via deep link."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="telegram_link_codes",
    )
    code = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"TelegramLinkCode({self.code[:8]}...) for {self.user_id}"

    @staticmethod
    def generate(*, user):
        """Create a fresh link token, removing any previous unused tokens."""
        TelegramLinkCode.objects.filter(user=user, is_used=False).delete()
        token = secrets.token_urlsafe(24)
        return TelegramLinkCode.objects.create(
            user=user,
            code=token,
            expires_at=timezone.now() + timedelta(minutes=10),
        )


class TelegramAuthCode(BaseModel):
    """One-time code for Telegram bot-based sign-in / sign-up.

    Flow:
    1. Frontend requests a code (no auth required)
    2. User opens t.me/bot?start=login_CODE in Telegram
    3. Bot receives /start login_CODE, captures telegram info, marks code as authenticated
    4. Frontend polls until authenticated, receives JWT tokens
    """

    code = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    # Set by the bot when user authenticates
    authenticated_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="telegram_auth_codes",
    )
    is_authenticated = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"TelegramAuthCode({self.code[:8]}...)"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate():
        """Create a fresh auth code (5-minute TTL)."""
        token = secrets.token_urlsafe(24)
        return TelegramAuthCode.objects.create(
            code=token,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

    @staticmethod
    def cleanup_expired():
        """Delete expired, unauthenticated codes to prevent DB bloat."""
        TelegramAuthCode.objects.filter(
            is_authenticated=False,
            expires_at__lt=timezone.now(),
        ).delete()
