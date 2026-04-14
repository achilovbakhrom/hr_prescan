"""Seed the four default subscription plans (Free, Starter, Professional, Enterprise)."""

from django.db import migrations


def seed_plans(apps, schema_editor):
    """Create default plans using the service helper logic (inlined for migration safety)."""
    from decimal import Decimal

    SubscriptionPlan = apps.get_model("subscriptions", "SubscriptionPlan")

    defaults = [
        {
            "tier": "free",
            "name": "Free",
            "description": "Get started with basic features",
            "price_monthly": Decimal("0.00"),
            "price_yearly": Decimal("0.00"),
            "max_vacancies": 2,
            "max_interviews_per_month": 10,
            "max_hr_users": 1,
            "max_storage_gb": 1,
        },
        {
            "tier": "starter",
            "name": "Starter",
            "description": "For small teams getting started with AI interviews",
            "price_monthly": Decimal("49.00"),
            "price_yearly": Decimal("470.00"),
            "max_vacancies": 10,
            "max_interviews_per_month": 50,
            "max_hr_users": 3,
            "max_storage_gb": 10,
        },
        {
            "tier": "professional",
            "name": "Professional",
            "description": "For growing teams with advanced needs",
            "price_monthly": Decimal("149.00"),
            "price_yearly": Decimal("1430.00"),
            "max_vacancies": 50,
            "max_interviews_per_month": 200,
            "max_hr_users": 10,
            "max_storage_gb": 50,
        },
        {
            "tier": "enterprise",
            "name": "Enterprise",
            "description": "Unlimited access for large organisations",
            "price_monthly": Decimal("399.00"),
            "price_yearly": Decimal("3830.00"),
            "max_vacancies": 0,  # unlimited
            "max_interviews_per_month": 0,  # unlimited
            "max_hr_users": 0,  # unlimited
            "max_storage_gb": 500,
        },
    ]

    for data in defaults:
        tier = data.pop("tier")
        SubscriptionPlan.objects.update_or_create(tier=tier, defaults=data)


def remove_plans(apps, schema_editor):
    """Remove seeded plans (reverse migration)."""
    SubscriptionPlan = apps.get_model("subscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(
        tier__in=["free", "starter", "professional", "enterprise"],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, remove_plans),
    ]
