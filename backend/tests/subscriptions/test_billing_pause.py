from datetime import timedelta
from decimal import Decimal

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from apps.subscriptions.services import check_and_expire_trials, check_vacancy_quota
from tests.factories import CompanyFactory, CompanyMembershipFactory, UserFactory


def _admin_with_company() -> User:
    admin = UserFactory(company=None, role=User.Role.ADMIN)
    company = CompanyFactory(account_owner=admin)
    admin.company = company
    admin.save(update_fields=["company", "updated_at"])
    CompanyMembershipFactory(user=admin, company=company, role=User.Role.ADMIN)
    return admin


def _plan(tier: str = SubscriptionPlan.Tier.PROFESSIONAL) -> SubscriptionPlan:
    return SubscriptionPlan.objects.create(
        tier=tier,
        name=tier.title(),
        description="Test plan",
        price_monthly=Decimal("10.00"),
        price_yearly=Decimal("100.00"),
        max_vacancies=1,
        max_interviews_per_month=1,
        max_hr_users=1,
        max_storage_gb=1,
    )


@override_settings(BILLING_ENABLED=False)
def test_quota_checks_pass_without_subscription_when_billing_paused():
    admin = _admin_with_company()

    assert check_vacancy_quota(user=admin) is True


@override_settings(BILLING_ENABLED=True)
def test_quota_checks_require_subscription_when_billing_enabled():
    admin = _admin_with_company()

    assert check_vacancy_quota(user=admin) is False


@override_settings(BILLING_ENABLED=False)
def test_subscription_changes_are_rejected_when_billing_paused():
    admin = _admin_with_company()
    plan = _plan()
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        "/api/hr/subscription/",
        {"plan_tier": plan.tier, "billing_period": UserSubscription.BillingPeriod.MONTHLY},
        format="json",
    )

    assert response.status_code == 403
    assert UserSubscription.objects.filter(user=admin).exists() is False


@override_settings(BILLING_ENABLED=False)
def test_expired_trials_are_not_downgraded_when_billing_paused():
    admin = _admin_with_company()
    admin.subscription_status = User.SubscriptionStatus.TRIAL
    admin.trial_ends_at = timezone.now() - timedelta(days=1)
    admin.save(update_fields=["subscription_status", "trial_ends_at", "updated_at"])

    assert check_and_expire_trials() == 0

    admin.refresh_from_db()
    assert admin.subscription_status == User.SubscriptionStatus.TRIAL
