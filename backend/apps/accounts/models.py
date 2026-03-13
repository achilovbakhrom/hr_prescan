import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Company(models.Model):
    """Company / tenant model."""

    class Size(models.TextChoices):
        SMALL = "small", "Small (1-50)"
        MEDIUM = "medium", "Medium (51-200)"
        LARGE = "large", "Large (201-1000)"
        ENTERPRISE = "enterprise", "Enterprise (1000+)"

    class SubscriptionStatus(models.TextChoices):
        TRIAL = "trial", "Trial"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    size = models.CharField(max_length=20, choices=Size.choices)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Subscription fields
    subscription_plan = models.ForeignKey(
        "self",  # placeholder — will be replaced with actual SubscriptionPlan model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIAL,
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "companies"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    """Custom user manager using email as the unique identifier."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
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
    phone = models.CharField(max_length=30, null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDATE)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


def _default_invitation_expiry() -> timezone.datetime:
    """Return default expiry: 7 days from now."""
    return timezone.now() + timedelta(days=7)


class Invitation(models.Model):
    """HR invitation to join a company."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
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
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=_default_invitation_expiry)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
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
