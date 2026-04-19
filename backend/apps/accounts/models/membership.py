import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from apps.accounts.models.user import User


class CompanyMembership(models.Model):
    """Tracks which companies a user belongs to, with per-company role & permissions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=User.Role.choices, default=User.Role.HR)
    hr_permissions = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounts"
        constraints = [
            models.UniqueConstraint(fields=["user", "company"], name="unique_user_company"),
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_default=True),
                name="unique_user_default_membership",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user.email} @ {self.company.name} ({self.role})"


def _default_invitation_expiry() -> timezone.datetime:
    """Return default expiry: 7 days from now."""
    return timezone.now() + timedelta(days=7)


class Invitation(models.Model):
    """HR invitation to join a company."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    token = models.UUIDField(unique=True, default=uuid.uuid4)
    permissions = models.JSONField(default=list, blank=True)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=_default_invitation_expiry)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "accounts"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"],
                condition=models.Q(is_accepted=False),
                name="unique_pending_invitation_per_company",
            ),
        ]

    def __str__(self) -> str:
        return f"Invitation for {self.email} to {self.company.name}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at
