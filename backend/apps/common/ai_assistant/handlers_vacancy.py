"""Handlers for vacancy-related AI assistant operations."""

from apps.common.ai_assistant.resolvers import resolve_vacancy


def handle_list_vacancies(*, user, params):
    from apps.vacancies.selectors import get_company_vacancies

    vacancies = get_company_vacancies(company=user.company, status=params.get("status"))
    total = vacancies.count()
    data = [
        {
            "id": str(v.id),
            "title": v.title,
            "status": v.status,
            "candidates_total": getattr(v, "candidates_total", None),
        }
        for v in vacancies[:20]
    ]
    msg = f"Found {total} vacanc{'y' if total == 1 else 'ies'}."
    if total > 20:
        msg += " Showing first 20."
    return {
        "success": True,
        "message": msg,
        "data": data,
        "action": "list_vacancies",
    }


def handle_create_vacancy(*, user, params):
    from apps.vacancies.models import EmployerCompany, Vacancy
    from apps.vacancies.services import create_vacancy

    # Prevent duplicate creation: if a draft vacancy with the same title exists, return it
    title = params.get("title", "Untitled").strip()
    existing = Vacancy.objects.filter(
        company=user.company, title__iexact=title, status=Vacancy.Status.DRAFT, is_deleted=False
    ).first()
    if existing:
        return {
            "success": True,
            "message": f"Vacancy '{existing.title}' already exists as a draft.",
            "data": {"id": str(existing.id), "title": existing.title},
            "action": "create_vacancy",
        }

    employer = None
    employer_name = (params.get("employer_name") or "").strip()

    # Ignore garbage/explanatory text the LLM may generate
    garbage_patterns = [
        "not provided",
        "not specified",
        "unknown",
        "couldn't",
        "could not",
        "n/a",
        "none",
        "no company",
    ]
    if employer_name and not any(p in employer_name.lower() for p in garbage_patterns):
        employer = EmployerCompany.objects.filter(company=user.company, name__icontains=employer_name).first()
        if not employer:
            employer = EmployerCompany.objects.create(company=user.company, name=employer_name)
    elif not employer_name:
        # Default to "Unknown" employer with empty description
        employer, _ = EmployerCompany.objects.get_or_create(
            company=user.company, name="Unknown", defaults={"description": ""}
        )

    kwargs = {}
    for field in (
        "salary_min",
        "salary_max",
        "salary_currency",
        "location",
        "is_remote",
        "employment_type",
        "experience_level",
    ):
        if params.get(field) is not None:
            kwargs[field] = params[field]
    # Skills come as comma-separated string from Gemini, convert to list
    skills_raw = params.get("skills")
    if skills_raw:
        if isinstance(skills_raw, str):
            kwargs["skills"] = [s.strip() for s in skills_raw.split(",") if s.strip()]
        else:
            kwargs["skills"] = skills_raw
    if employer:
        kwargs["employer"] = employer

    vacancy = create_vacancy(
        company=user.company,
        created_by=user,
        title=title,
        description=params.get("description", ""),
        **kwargs,
    )
    return {
        "success": True,
        "message": f"Created vacancy '{vacancy.title}'.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "create_vacancy",
    }


def handle_update_vacancy(*, user, params):
    from apps.vacancies.services import update_vacancy

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    updates = params.get("updates", {})
    if not updates:
        return {
            "success": False,
            "message": (
                f"No updates provided for vacancy '{vacancy.title}'. You must pass the 'updates' parameter "
                f'with fields to change, e.g. updates={{"title": "New Title"}}.'
            ),
            "data": {"id": str(vacancy.id), "title": vacancy.title},
        }
    vacancy = update_vacancy(vacancy=vacancy, data=updates)
    return {
        "success": True,
        "message": f"Updated vacancy '{vacancy.title}'. Changed: {', '.join(updates.keys())}.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "update_vacancy",
    }


def handle_publish_vacancy(*, user, params):
    from apps.vacancies.services import publish_vacancy

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = publish_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' is now published.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "publish_vacancy",
    }


def handle_pause_vacancy(*, user, params):
    from apps.vacancies.services import pause_vacancy

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = pause_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' is now paused.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "pause_vacancy",
    }


def handle_archive_vacancy(*, user, params):
    from apps.vacancies.services import archive_vacancy

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = archive_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' has been archived.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "archive_vacancy",
    }


def handle_delete_vacancy(*, user, params):
    from apps.vacancies.services import soft_delete_vacancy

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    soft_delete_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' has been deleted.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "delete_vacancy",
    }


def handle_generate_questions(*, user, params):
    from apps.vacancies.services import generate_interview_questions

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    step = params.get("step", "prescanning")
    questions = generate_interview_questions(vacancy=vacancy, step=step)
    data = [{"text": q.text, "category": q.category} for q in questions]
    return {
        "success": True,
        "message": f"Generated {len(data)} {step} questions for '{vacancy.title}'.",
        "data": data,
        "action": "generate_questions",
    }


def handle_regenerate_keywords(*, user, params):
    from apps.vacancies.services import generate_vacancy_keywords

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    keywords = generate_vacancy_keywords(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Regenerated {len(keywords)} keywords for '{vacancy.title}'.",
        "data": {"keywords": keywords},
        "action": "regenerate_keywords",
    }
