from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import Company
from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore


def get_company_interviews(
    *,
    company: Company,
    status: str | None = None,
) -> QuerySet[Interview]:
    """Return interviews for a company, optionally filtered by status."""
    qs = (
        Interview.objects
        .filter(application__vacancy__company=company)
        .select_related(
            "application",
            "application__vacancy",
            "application__candidate",
        )
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_interview_by_id(
    *,
    interview_id: UUID,
    company: Company | None = None,
) -> Interview | None:
    """Get a single interview, optionally scoped to a company."""
    qs = Interview.objects.select_related(
        "application",
        "application__vacancy",
        "application__vacancy__company",
        "application__candidate",
    )
    if company:
        qs = qs.filter(application__vacancy__company=company)
    return qs.filter(id=interview_id).first()


def get_interview_by_token(
    *,
    interview_token: UUID,
) -> Interview | None:
    """Get an interview by its unique interview_token (for candidate access)."""
    return (
        Interview.objects
        .select_related(
            "application",
            "application__vacancy",
            "application__vacancy__company",
            "application__vacancy__employer",
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
        Interview.objects
        .select_related(
            "application",
            "application__vacancy",
            "application__vacancy__company",
            "application__vacancy__employer",
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
    return (
        InterviewScore.objects
        .filter(interview=interview)
        .select_related("criteria")
        .order_by("criteria__order")
    )


def get_interview_integrity_flags(
    *,
    interview: Interview,
) -> QuerySet[InterviewIntegrityFlag]:
    """Return integrity flags for an interview."""
    return (
        InterviewIntegrityFlag.objects
        .filter(interview=interview)
        .order_by("timestamp_seconds")
    )


def get_integrity_flags(
    *,
    interview_id: UUID,
    company: Company | None = None,
) -> QuerySet[InterviewIntegrityFlag] | None:
    """Return integrity flags for an interview by ID, optionally scoped to a company.

    Returns None if the interview does not exist (or does not belong to the company).
    """
    interview_qs = Interview.objects.filter(id=interview_id)
    if company:
        interview_qs = interview_qs.filter(application__vacancy__company=company)

    interview = interview_qs.first()
    if interview is None:
        return None

    return (
        InterviewIntegrityFlag.objects
        .filter(interview=interview)
        .order_by("timestamp_seconds")
    )
