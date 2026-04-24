from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import Company, User
from apps.accounts.selectors import get_user_live_company_ids
from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore


def get_company_interviews(
    *,
    company: Company,
    status: str | None = None,
) -> QuerySet[Interview]:
    """Return interviews for a company, optionally filtered by status."""
    qs = Interview.objects.filter(application__vacancy__company=company).select_related(
        "application",
        "application__vacancy",
        "application__candidate",
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_user_interviews(
    *,
    user: User,
    status: str | None = None,
) -> QuerySet[Interview]:
    """Return interviews across every non-deleted company the user belongs to."""
    qs = Interview.objects.filter(
        application__vacancy__company_id__in=get_user_live_company_ids(user=user),
    ).select_related(
        "application",
        "application__vacancy",
        "application__candidate",
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_interview_by_id(
    *,
    interview_id: UUID,
    company: Company | None = None,
    user: User | None = None,
) -> Interview | None:
    """Get a single interview, scoped to a company or any company the user belongs to."""
    qs = Interview.objects.select_related(
        "application",
        "application__vacancy",
        "application__vacancy__company",
        "application__candidate",
    )
    if user:
        qs = qs.filter(application__vacancy__company_id__in=get_user_live_company_ids(user=user))
    elif company:
        qs = qs.filter(application__vacancy__company=company)
    return qs.filter(id=interview_id).first()


def get_interview_by_token(
    *,
    interview_token: UUID,
) -> Interview | None:
    """Get an interview by its unique interview_token (for candidate access)."""
    return (
        Interview.objects.select_related(
            "application",
            "application__vacancy",
            "application__vacancy__company",
            "application__candidate",
        )
        .filter(interview_token=interview_token)
        .first()
    )


def get_interview_for_candidate(
    *,
    interview_id: UUID,
    candidate_email: str,
) -> Interview | None:
    """Get an interview for a candidate accessing their own interview."""
    return (
        Interview.objects.select_related(
            "application",
            "application__vacancy",
            "application__vacancy__company",
        )
        .filter(
            id=interview_id,
            application__candidate_email=candidate_email,
        )
        .first()
    )


def get_interview_scores(
    *,
    interview: Interview,
) -> QuerySet[InterviewScore]:
    """Return scores for an interview with related criteria."""
    return InterviewScore.objects.filter(interview=interview).select_related("criteria").order_by("criteria__order")


def get_interview_integrity_flags(
    *,
    interview: Interview,
) -> QuerySet[InterviewIntegrityFlag]:
    """Return integrity flags for an interview."""
    return InterviewIntegrityFlag.objects.filter(interview=interview).order_by("timestamp_seconds")


def get_integrity_flags(
    *,
    interview_id: UUID,
    company: Company | None = None,
    user: User | None = None,
) -> QuerySet[InterviewIntegrityFlag] | None:
    """Return integrity flags for an interview by ID, scoped to a company or user.

    Returns None if the interview does not exist or is out of scope.
    """
    interview_qs = Interview.objects.filter(id=interview_id)
    if user:
        interview_qs = interview_qs.filter(application__vacancy__company_id__in=get_user_live_company_ids(user=user))
    elif company:
        interview_qs = interview_qs.filter(application__vacancy__company=company)

    interview = interview_qs.first()
    if interview is None:
        return None

    return InterviewIntegrityFlag.objects.filter(interview=interview).order_by("timestamp_seconds")
