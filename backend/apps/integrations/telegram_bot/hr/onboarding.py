"""Telegram-first HR/admin onboarding helpers."""

from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.accounts.models import Company, CompanyMembership, Invitation, User
from apps.integrations.models import TelegramLinkCode
from apps.notifications.models import Message, Notification
from apps.subscriptions.models import UserSubscription
from apps.vacancies.models import Vacancy


def hr_placeholder_email(*, telegram_id: int) -> str:
    return f"tg_hr_{telegram_id}@telegram.local"


def is_hr_placeholder(*, user: User, telegram_id: int) -> bool:
    return (
        user.role == User.Role.ADMIN
        and user.email == hr_placeholder_email(telegram_id=telegram_id)
        and user.telegram_id == telegram_id
    )


def get_or_create_hr_bot_user(
    *,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",
    last_name: str = "",
    language: str = User.Language.EN,
) -> User:
    user = User.objects.filter(telegram_id=telegram_id, role__in=[User.Role.ADMIN, User.Role.HR]).first()
    if user is not None:
        return user

    email = hr_placeholder_email(telegram_id=telegram_id)
    try:
        user = User.objects.create_user(
            email=email,
            password=None,
            first_name=first_name or "Telegram",
            last_name=last_name or "Admin",
            role=User.Role.ADMIN,
            email_verified=False,
        )
    except IntegrityError:
        user = User.objects.get(email=email)

    user.telegram_id = telegram_id
    user.telegram_username = telegram_username
    if language in User.Language.values:
        user.language = language
    user.onboarding_completed = False
    user.save(update_fields=["telegram_id", "telegram_username", "language", "onboarding_completed", "updated_at"])
    return user


@transaction.atomic
def merge_hr_placeholder(*, source: User, target: User) -> None:
    """Move Telegram-first HR workspace data to the confirmed web account."""
    owner = target.effective_account_owner
    User.objects.filter(account_owner=source).update(account_owner=owner)
    Company.objects.filter(account_owner=source).update(account_owner=owner)
    Vacancy.objects.filter(created_by=source).update(created_by=target)
    Invitation.objects.filter(account_owner=source).update(account_owner=owner)
    Invitation.objects.filter(invited_by=source).update(invited_by=target)
    Notification.objects.filter(user=source).update(user=target)
    Message.objects.filter(sender=source).update(sender=target)
    Message.objects.filter(recipient=source).update(recipient=target)
    TelegramLinkCode.objects.filter(user=source, is_used=False).delete()

    _move_memberships(source=source, target=target)
    _move_subscription(source=source, target=target)
    _activate_default_membership(user=target)
    _merge_language(source=source, target=target)

    source.telegram_id = None
    source.telegram_username = ""
    source.is_active = False
    source.company = None
    source.save(update_fields=["telegram_id", "telegram_username", "is_active", "company", "updated_at"])


def _merge_language(*, source: User, target: User) -> None:
    if source.language and source.language != target.language:
        target.language = source.language
        target.save(update_fields=["language", "updated_at"])


def _move_memberships(*, source: User, target: User) -> None:
    target_has_default = CompanyMembership.objects.filter(user=target, is_default=True).exists()
    for membership in CompanyMembership.objects.filter(user=source).select_related("company").order_by("-is_default"):
        source_was_default = membership.is_default
        membership.is_default = False
        membership.save(update_fields=["is_default"])

        if CompanyMembership.objects.filter(user=target, company=membership.company).exists():
            membership.delete()
            continue

        membership.user = target
        membership.is_default = source_was_default and not target_has_default
        membership.save(update_fields=["user", "is_default"])
        target_has_default = target_has_default or membership.is_default


def _move_subscription(*, source: User, target: User) -> None:
    source_subscription = UserSubscription.objects.filter(user=source).first()
    if source_subscription is None:
        return
    if UserSubscription.objects.filter(user=target).exists():
        source_subscription.delete()
        return
    source_subscription.user = target
    source_subscription.save(update_fields=["user", "updated_at"])


def _activate_default_membership(*, user: User) -> None:
    membership = (
        CompanyMembership.objects.filter(user=user, company__is_deleted=False, is_default=True)
        .select_related("company")
        .first()
    )
    if membership is None:
        membership = (
            CompanyMembership.objects.filter(user=user, company__is_deleted=False)
            .select_related("company")
            .order_by("created_at")
            .first()
        )
        if membership is None:
            return
        membership.is_default = True
        membership.save(update_fields=["is_default"])

    user.company = membership.company
    user.role = membership.role
    user.hr_permissions = membership.hr_permissions
    user.save(update_fields=["company", "role", "hr_permissions", "updated_at"])
