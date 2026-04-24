"""Merge a bot-created candidate placeholder into a real web candidate account."""

from __future__ import annotations

from apps.accounts.models import (
    CandidateCV,
    CandidateLanguage,
    CandidateProfile,
    Certification,
    Education,
    User,
    WorkExperience,
)
from apps.applications.models import Application
from apps.integrations.models import TelegramLinkCode
from apps.notifications.models import Message, Notification


def merge_candidate_accounts(*, source: User, target: User) -> None:
    """Move candidate-owned data from a Telegram placeholder account to target."""
    _merge_profile(source=source, target=target)
    _merge_language(source=source, target=target)
    Application.objects.filter(candidate=source).update(candidate=target)
    Notification.objects.filter(user=source).update(user=target)
    Message.objects.filter(sender=source).update(sender=target)
    Message.objects.filter(recipient=source).update(recipient=target)
    TelegramLinkCode.objects.filter(user=source, is_used=False).delete()

    source.telegram_id = None
    source.telegram_username = ""
    source.is_active = False
    source.save(update_fields=["telegram_id", "telegram_username", "is_active", "updated_at"])


def _merge_language(*, source: User, target: User) -> None:
    if source.language and source.language != target.language:
        target.language = source.language
        target.save(update_fields=["language", "updated_at"])


def _merge_profile(*, source: User, target: User) -> None:
    source_profile = CandidateProfile.objects.filter(user=source).first()
    if source_profile is None:
        return

    target_profile = CandidateProfile.objects.filter(user=target).first()
    if target_profile is None:
        source_profile.user = target
        source_profile.save(update_fields=["user", "updated_at"])
        return

    _fill_blank_profile_fields(source=source_profile, target=target_profile)
    target_profile.skills.add(*source_profile.skills.all())

    WorkExperience.objects.filter(profile=source_profile).update(profile=target_profile)
    Education.objects.filter(profile=source_profile).update(profile=target_profile)
    Certification.objects.filter(profile=source_profile).update(profile=target_profile)
    CandidateCV.objects.filter(profile=source_profile).update(profile=target_profile)
    _merge_languages(source=source_profile, target=target_profile)
    _normalize_active_cv(profile=target_profile)
    source_profile.delete()


def _fill_blank_profile_fields(*, source: CandidateProfile, target: CandidateProfile) -> None:
    fields = [
        "headline",
        "summary",
        "location",
        "date_of_birth",
        "linkedin_url",
        "github_url",
        "website_url",
        "desired_salary_min",
        "desired_salary_max",
        "desired_salary_currency",
        "desired_salary_negotiable",
        "desired_employment_type",
        "is_open_to_work",
        "photo",
    ]
    changed: list[str] = []
    for field in fields:
        target_value = getattr(target, field)
        source_value = getattr(source, field)
        if _is_empty(target_value) and not _is_empty(source_value):
            setattr(target, field, source_value)
            changed.append(field)
    if changed:
        target.save(update_fields=[*changed, "updated_at"])


def _is_empty(value) -> bool:
    return value is None or value == "" or value is False


def _merge_languages(*, source: CandidateProfile, target: CandidateProfile) -> None:
    existing_language_ids = set(CandidateLanguage.objects.filter(profile=target).values_list("language_id", flat=True))
    for language in CandidateLanguage.objects.filter(profile=source):
        if language.language_id in existing_language_ids:
            language.delete()
            continue
        language.profile = target
        language.save(update_fields=["profile", "updated_at"])
        existing_language_ids.add(language.language_id)


def _normalize_active_cv(*, profile: CandidateProfile) -> None:
    active_ids = list(CandidateCV.objects.filter(profile=profile, is_active=True).values_list("id", flat=True))
    if len(active_ids) <= 1:
        return
    CandidateCV.objects.filter(profile=profile, is_active=True).exclude(id=active_ids[0]).update(is_active=False)
