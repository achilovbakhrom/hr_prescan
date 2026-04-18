from apps.common.exceptions import ApplicationError


def _handle_search_jobs(*, user, params):
    from apps.vacancies.selectors import get_public_vacancies

    query = params.get("query")
    location = params.get("location")
    is_remote = params.get("is_remote")
    skills_raw = params.get("skills")

    # Build search query from multiple inputs
    search_terms = []
    if query:
        search_terms.append(query)
    if skills_raw:
        search_terms.append(skills_raw)

    search = " ".join(search_terms) if search_terms else None

    vacancies = get_public_vacancies(
        search=search,
        location=location,
        is_remote=is_remote,
    )

    total = vacancies.count()
    data = [
        {
            "id": str(v.id),
            "title": v.title,
            "company": v.company.name if v.company else "",
            "employer": v.employer.name if v.employer else "",
            "location": v.location,
            "is_remote": v.is_remote,
            "employment_type": v.employment_type,
            "experience_level": v.experience_level,
            "salary_min": float(v.salary_min) if v.salary_min else None,
            "salary_max": float(v.salary_max) if v.salary_max else None,
            "salary_currency": v.salary_currency,
            "skills": v.skills or [],
        }
        for v in vacancies[:20]
    ]

    msg = f"Found {total} job{'s' if total != 1 else ''} matching your search."
    if total == 0:
        msg = "No jobs found matching your criteria. Try broadening your search."
    elif total > 20:
        msg += " Showing the top 20 results."

    return {
        "success": True,
        "message": msg,
        "data": data,
        "action": "search_jobs",
    }


def _handle_get_job_details(*, user, params):
    from apps.vacancies.models import Vacancy

    vacancy_id = params.get("vacancy_id", "")
    try:
        vacancy = Vacancy.objects.select_related("company", "employer").get(
            id=vacancy_id,
            status=Vacancy.Status.PUBLISHED,
            is_deleted=False,
        )
    except (Vacancy.DoesNotExist, ValueError):
        raise ApplicationError("Job not found. It may have been removed or is no longer available.") from None

    data = {
        "id": str(vacancy.id),
        "title": vacancy.title,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "responsibilities": vacancy.responsibilities,
        "company": vacancy.company.name if vacancy.company else "",
        "employer": vacancy.employer.name if vacancy.employer else "",
        "location": vacancy.location,
        "is_remote": vacancy.is_remote,
        "employment_type": vacancy.employment_type,
        "experience_level": vacancy.experience_level,
        "salary_min": float(vacancy.salary_min) if vacancy.salary_min else None,
        "salary_max": float(vacancy.salary_max) if vacancy.salary_max else None,
        "salary_currency": vacancy.salary_currency,
        "skills": vacancy.skills or [],
        "cv_required": vacancy.cv_required,
        "interview_mode": vacancy.interview_mode,
    }

    return {
        "success": True,
        "message": f"Details for '{vacancy.title}'.",
        "data": data,
        "action": "get_job_details",
    }
