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
