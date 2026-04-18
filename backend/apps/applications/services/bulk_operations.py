from uuid import UUID

from django.db import transaction
from django.db.models import Q

from apps.accounts.models import User
from apps.applications.models import Application
from apps.applications.services.application_crud import STATUS_TRANSITIONS
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_STATUS_TRANSITION_INVALID


@transaction.atomic
def bulk_update_status(
    *,
    application_ids: list[UUID],
    status: str,
    updated_by: User,
) -> int:
    """Update multiple applications to a new status. Returns count of updated records.

    Only transitions that are valid per STATUS_TRANSITIONS are applied;
    applications that cannot transition are silently skipped.
    """
    from apps.notifications.services import notify_status_changed

    applications = Application.objects.filter(
        id__in=application_ids,
        vacancy__company=updated_by.company,
    ).select_related("vacancy")

    updated = 0
    for application in applications:
        allowed = STATUS_TRANSITIONS.get(application.status, set())
        if status not in allowed:
            continue

        application.status = status
        application.save(update_fields=["status", "updated_at"])

        notify_status_changed(application=application)
        updated += 1

    return updated


def soft_delete_applications(
    *,
    application_ids: list[UUID],
    updated_by: User,
) -> int:
    """Soft-delete applications (clear from archive). Completely hidden from UI."""
    from django.utils import timezone

    return Application.objects.filter(
        id__in=application_ids,
        vacancy__company=updated_by.company,
        status=Application.Status.ARCHIVED,
    ).update(is_deleted=True, updated_at=timezone.now())


def bulk_move_by_filter(
    *,
    vacancy_id: UUID,
    from_status: str,
    to_status: str,
    updated_by: User,
    max_score: float | None = None,
    min_score: float | None = None,
    score_field: str = "match_score",
    has_cv: bool | None = None,
    days_since_applied: int | None = None,
) -> int:
    """Batch move candidates from one status to another with optional filters.

    Args:
        from_status: Source status to filter candidates.
        to_status: Target status to move to.
        max_score: Only include candidates with score < this value.
        min_score: Only include candidates with score > this value.
        score_field: Which score to filter by: match_score, prescanning_score, interview_score.
        has_cv: Filter by whether candidate has a CV.
        days_since_applied: Only include candidates applied more than X days ago.
    """
    from datetime import timedelta

    from django.utils import timezone as tz

    # Validate transition
    allowed = STATUS_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise ApplicationError(str(MSG_STATUS_TRANSITION_INVALID).format(current=from_status, target=to_status))

    qs = Application.objects.filter(
        vacancy_id=vacancy_id,
        vacancy__company=updated_by.company,
        status=from_status,
        is_deleted=False,
    )

    # Score filters -- for prescanning/interview scores, join through sessions
    if score_field == "match_score":
        if max_score is not None:
            qs = qs.filter(match_score__lt=max_score)
        if min_score is not None:
            qs = qs.filter(match_score__gt=min_score)
    elif score_field in ("prescanning_score", "interview_score"):
        session_type = "prescanning" if score_field == "prescanning_score" else "interview"
        session_filter = Q(
            sessions__session_type=session_type,
            sessions__status="completed",
        )
        if max_score is not None:
            session_filter &= Q(sessions__overall_score__lt=max_score)
        if min_score is not None:
            session_filter &= Q(sessions__overall_score__gt=min_score)
        qs = qs.filter(session_filter).distinct()

    if has_cv is True:
        qs = qs.exclude(cv_file="")
    elif has_cv is False:
        qs = qs.filter(cv_file="")

    if days_since_applied is not None:
        cutoff = tz.now() - timedelta(days=days_since_applied)
        qs = qs.filter(created_at__lt=cutoff)

    count = qs.update(status=to_status)
    return count


def add_hr_note(*, application: Application, note: str) -> Application:
    """Append a note to the application's HR notes."""
    if application.hr_notes:
        application.hr_notes += f"\n\n---\n\n{note}"
    else:
        application.hr_notes = note

    application.save(update_fields=["hr_notes", "updated_at"])
    return application


def bind_existing_applications(*, user: User) -> int:
    """Bind anonymous applications to a newly registered user.

    Finds Applications where candidate_email (case-insensitive) matches
    user.email OR candidate_phone matches user.phone (if user has a phone),
    and candidate is NULL. Sets candidate=user on matching records.

    Returns the number of applications bound.
    """
    filter_q = Q(candidate__isnull=True, candidate_email__iexact=user.email)
    if user.phone:
        filter_q |= Q(candidate__isnull=True, candidate_phone=user.phone)

    return Application.objects.filter(filter_q).update(candidate=user)
