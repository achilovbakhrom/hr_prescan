import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.common.models import BaseModel


class TelegramLinkCode(BaseModel):
    """One-time 6-digit code for linking a Telegram account to a platform user."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="telegram_link_codes",
    )
    code = models.CharField(max_length=6, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"TelegramLinkCode({self.code}) for {self.user_id}"

    @staticmethod
    def generate(*, user):
        """Create a fresh 6-digit link code, removing any previous unused codes."""
        # Delete old unused codes for this user
        TelegramLinkCode.objects.filter(user=user, is_used=False).delete()
        code = "".join(str(secrets.randbelow(10)) for _ in range(6))
        return TelegramLinkCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=10),
        )
