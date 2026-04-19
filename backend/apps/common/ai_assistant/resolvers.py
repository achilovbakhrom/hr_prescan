"""Resolvers: fuzzy-match helpers for vacancies, companies, applications, interviews."""

from apps.common.exceptions import ApplicationError


def _user_live_company_ids(user):
    return list(user.memberships.filter(company__is_deleted=False).values_list("company_id", flat=True))


def resolve_vacancy(*, user, title):
    """Find a vacancy by fuzzy title match across every company the user belongs to."""
    from apps.vacancies.models import Vacancy

    matches = list(
        Vacancy.objects.filter(
            company_id__in=_user_live_company_ids(user),
            is_deleted=False,
            title__icontains=title,
        ).values_list("id", "title")[:10]
    )
    if not matches:
        raise ApplicationError(f"Vacancy matching '{title}' not found.")
    if len(matches) > 1:
        names = ", ".join(f'"{m[1]}"' for m in matches)
        raise ApplicationError(f"Multiple vacancies match '{title}': {names}. Please be more specific.")
    return Vacancy.objects.get(id=matches[0][0])


def resolve_company(*, user, name):
    """Find one of the user's non-deleted companies by fuzzy name match."""
    from apps.accounts.models import Company

    matches = list(
        Company.objects.filter(
            id__in=_user_live_company_ids(user),
            name__icontains=name,
        ).values_list("id", "name")[:10]
    )
    if not matches:
        raise ApplicationError(f"Company matching '{name}' not found.")
    if len(matches) > 1:
        names = ", ".join(f'"{m[1]}"' for m in matches)
        raise ApplicationError(f"Multiple companies match '{name}': {names}. Please be more specific.")
    return Company.objects.get(id=matches[0][0])


def resolve_application(*, user, candidate_email_or_name, vacancy_title=None):
    """Find an application by candidate email or name across the user's companies."""
    from apps.applications.models import Application

    qs = Application.objects.filter(
        vacancy__company_id__in=_user_live_company_ids(user),
        is_deleted=False,
    ).select_related("vacancy")

    if vacancy_title:
        qs = qs.filter(vacancy__title__icontains=vacancy_title)

    # Try email match first, then name
    matches = list(
        qs.filter(candidate_email__icontains=candidate_email_or_name).values_list(
            "id", "candidate_name", "candidate_email"
        )[:10]
    )
    if not matches:
        matches = list(
            qs.filter(candidate_name__icontains=candidate_email_or_name).values_list(
                "id", "candidate_name", "candidate_email"
            )[:10]
        )
    if not matches:
        raise ApplicationError(f"Candidate matching '{candidate_email_or_name}' not found.")
    if len(matches) > 1:
        names = ", ".join(f"{m[1]} ({m[2]})" for m in matches)
        raise ApplicationError(
            f"Multiple candidates match '{candidate_email_or_name}': {names}. Please be more specific (use email)."
        )
    return Application.objects.select_related("vacancy").get(id=matches[0][0])


def resolve_interview_for_candidate(*, user, candidate_email_or_name):
    """Find the most recent active interview for a candidate, across the user's companies."""
    from django.db.models import Q

    from apps.interviews.models import Interview

    qs = (
        Interview.objects.filter(
            application__vacancy__company_id__in=_user_live_company_ids(user),
            application__is_deleted=False,
        )
        .select_related("application", "application__vacancy")
        .order_by("-created_at")
    )

    interview = qs.filter(
        Q(application__candidate_email__icontains=candidate_email_or_name)
        | Q(application__candidate_name__icontains=candidate_email_or_name)
    ).first()
    if interview is None:
        raise ApplicationError(f"No interview found for candidate matching '{candidate_email_or_name}'.")
    return interview
