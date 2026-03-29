import uuid

from django.db import models


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
    industries = models.ManyToManyField(
        "common.Industry",
        blank=True,
        related_name="companies",
    )
    size = models.CharField(max_length=20, choices=Size.choices)
    country = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)  # noqa: DJ001
    description = models.TextField(null=True, blank=True)  # noqa: DJ001

    # Subscription fields
    subscription_plan = models.ForeignKey(
        "subscriptions.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
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
        app_label = "accounts"
        verbose_name_plural = "companies"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
