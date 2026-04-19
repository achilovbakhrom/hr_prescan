from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager using email as the unique identifier."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> User:
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the username field."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        HR = "hr", "HR Manager"
        CANDIDATE = "candidate", "Candidate"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, null=True, blank=True)  # noqa: DJ001
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE)
    company = models.ForeignKey(
        "accounts.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # Account owner: the user whose subscription and companies this user shares.
    # NULL means "I am my own account owner" (self-owned). For invited HR members,
    # this points to the owner whose Companies they were invited into.
    account_owner = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_members",
    )

    class SubscriptionStatus(models.TextChoices):
        TRIAL = "trial", "Trial"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELLED = "cancelled", "Cancelled"

    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    # Onboarding -- False for new social auth users until they pick a role
    onboarding_completed = models.BooleanField(default=True)

    # HR granular permissions (only applies when role="hr")
    # Admin role always has all permissions regardless of this field.
    hr_permissions = models.JSONField(default=list, blank=True)

    # Telegram integration
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = models.CharField(max_length=255, blank=True, default="")

    # UI language — source of truth for AI assistants and default vacancy language.
    # Kept in sync with the frontend locale via PATCH /api/auth/me/, and seeded
    # on first visit from IP-based GeoIP detection for anonymous users.
    class Language(models.TextChoices):
        EN = "en", "English"
        RU = "ru", "Russian"
        UZ = "uz", "Uzbek"

    language = models.CharField(
        max_length=5,
        choices=Language.choices,
        default=Language.EN,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        app_label = "accounts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def effective_account_owner(self) -> User:
        """The user whose subscription and companies this user operates under."""
        return self.account_owner or self
