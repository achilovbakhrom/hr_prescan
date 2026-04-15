"""Resolvers: fuzzy-match helpers for vacancies, employers, applications, interviews."""

from apps.common.exceptions import ApplicationError


def resolve_vacancy(*, company, title):
    """Find a vacancy by fuzzy title match. Raises if ambiguous or not found."""
    from apps.vacancies.models import Vacancy

    matches = list(
        Vacancy.objects.filter(company=company, is_deleted=False, title__icontains=title).values_list("id", "title")[
            :10
        ]
    )
    if not matches:
        raise ApplicationError(f"Vacancy matching '{title}' not found.")
    if len(matches) > 1:
        names = ", ".join(f'"{m[1]}"' for m in matches)
        raise ApplicationError(f"Multiple vacancies match '{title}': {names}. Please be more specific.")
    return Vacancy.objects.get(id=matches[0][0])


def resolve_employer(*, company, name):
    """Find an employer by fuzzy name match. Raises if ambiguous or not found."""
    from apps.vacancies.models import EmployerCompany

    matches = list(EmployerCompany.objects.filter(company=company, name__icontains=name).values_list("id", "name")[:10])
    if not matches:
        raise ApplicationError(f"Employer matching '{name}' not found.")
    if len(matches) > 1:
        names = ", ".join(f'"{m[1]}"' for m in matches)
        raise ApplicationError(f"Multiple employers match '{name}': {names}. Please be more specific.")
    return EmployerCompany.objects.get(id=matches[0][0])


def resolve_application(*, company, candidate_email_or_name, vacancy_title=None):
    """Find an application by candidate email or name. Raises if ambiguous."""
    from apps.applications.models import Application

    qs = Application.objects.filter(
        vacancy__company=company,
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


def resolve_interview_for_candidate(*, company, candidate_email_or_name):
    """Find the most recent active interview for a candidate."""
    from django.db.models import Q

    from apps.interviews.models import Interview

    qs = (
        Interview.objects.filter(
            application__vacancy__company=company,
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
