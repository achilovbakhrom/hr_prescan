from django.db import models

from apps.common.models import BaseModel


class SubscriptionPlan(BaseModel):
    """Available subscription tiers."""

    class Tier(models.TextChoices):
        FREE = "free", "Free"
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=Tier.choices, unique=True)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    max_vacancies = models.IntegerField(default=0, help_text="0 = unlimited")
    max_interviews_per_month = models.IntegerField(default=0, help_text="0 = unlimited")
    max_hr_users = models.IntegerField(default=1)
    max_storage_gb = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self) -> str:
        return f"{self.name} ({self.tier})"


class CompanySubscription(BaseModel):
    """Active subscription linking a company to a plan."""

    class BillingPeriod(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    company = models.OneToOneField(
        "accounts.Company",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    billing_period = models.CharField(
        max_length=10,
        choices=BillingPeriod.choices,
        default=BillingPeriod.MONTHLY,
    )
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.company.name} — {self.plan.name} ({self.billing_period})"
