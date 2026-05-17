from django.db import transaction
from django.db.models import Min
from django.utils import timezone

from apps.applications.models import Application, HRCandidate


def normalize_candidate_email(email: str) -> str:
    return email.strip().lower()


def _latest_application(*, account_owner_id, email: str) -> Application | None:
    return (
        Application.objects.filter(
            vacancy__company__account_owner_id=account_owner_id,
            candidate_email__iexact=email,
            is_deleted=False,
        )
        .select_related("candidate", "vacancy", "vacancy__company")
        .order_by("-created_at", "-updated_at")
        .first()
    )


@transaction.atomic
def sync_hr_candidate_for_application(*, application: Application) -> HRCandidate | None:
    """Upsert the HR candidate-base row for an application."""
    if not application.candidate_email:
        return None

    application = (
        Application.objects.select_related("candidate", "vacancy", "vacancy__company").filter(id=application.id).first()
    )
    if application is None:
        return None

    account_owner = application.vacancy.company.account_owner
    normalized_email = normalize_candidate_email(application.candidate_email)
    first_seen_at = (
        Application.objects.filter(
            vacancy__company__account_owner=account_owner,
            candidate_email__iexact=normalized_email,
        ).aggregate(first_seen=Min("created_at"))["first_seen"]
        or application.created_at
        or timezone.now()
    )
    latest = _latest_application(account_owner_id=account_owner.id, email=normalized_email) or application
    latest_activity = latest.updated_at or latest.created_at or timezone.now()

    existing = (
        HRCandidate.objects.select_for_update()
        .filter(account_owner=account_owner, candidate_email_normalized=normalized_email)
        .order_by("is_deleted", "-updated_at")
        .first()
    )

    if existing is None:
        return HRCandidate.objects.create(
            account_owner=account_owner,
            candidate=application.candidate,
            candidate_name=application.candidate_name,
            candidate_email=application.candidate_email,
            candidate_email_normalized=normalized_email,
            candidate_phone=application.candidate_phone,
            latest_application=latest,
            first_seen_at=first_seen_at,
            last_activity_at=latest_activity,
        )

    existing.candidate = application.candidate or existing.candidate
    existing.candidate_name = application.candidate_name or existing.candidate_name
    existing.candidate_email = application.candidate_email
    existing.candidate_email_normalized = normalized_email
    existing.candidate_phone = application.candidate_phone or existing.candidate_phone
    existing.latest_application = latest
    existing.first_seen_at = min(existing.first_seen_at, first_seen_at)
    existing.last_activity_at = latest_activity
    existing.is_deleted = False
    existing.save(
        update_fields=[
            "candidate",
            "candidate_name",
            "candidate_email",
            "candidate_email_normalized",
            "candidate_phone",
            "latest_application",
            "first_seen_at",
            "last_activity_at",
            "is_deleted",
            "updated_at",
        ],
    )
    return existing
