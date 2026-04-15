"""Handlers for employer-related AI assistant operations."""

from apps.common.ai_assistant.resolvers import resolve_employer


def handle_list_employers(*, user, params):
    from apps.vacancies.selectors import get_company_employers

    employers = get_company_employers(company=user.company)
    data = [
        {
            "id": str(e.id),
            "name": e.name,
            "industry": e.industry,
            "website": e.website,
        }
        for e in employers[:20]
    ]
    return {
        "success": True,
        "message": f"Found {len(data)} employer{'s' if len(data) != 1 else ''}.",
        "data": data,
        "action": "list_employers",
    }


def handle_create_employer(*, user, params):
    from apps.vacancies.services import create_employer

    kwargs = {}
    for field in ("industry", "website", "description"):
        if params.get(field):
            kwargs[field] = params[field]

    employer = create_employer(
        company=user.company,
        name=params.get("name", "Unnamed"),
        **kwargs,
    )
    return {
        "success": True,
        "message": f"Created employer '{employer.name}'.",
        "data": {"id": str(employer.id), "name": employer.name},
        "action": "create_employer",
    }


def handle_create_employer_from_url(*, user, params):
    from apps.vacancies.services import create_employer_from_url

    employer = create_employer_from_url(
        company=user.company,
        name=params.get("name", "Unnamed"),
        url=params.get("url", ""),
    )
    return {
        "success": True,
        "message": f"Created employer '{employer.name}' from URL.",
        "data": {"id": str(employer.id), "name": employer.name},
        "action": "create_employer_from_url",
    }


def handle_update_employer(*, user, params):
    from apps.vacancies.services import update_employer

    employer = resolve_employer(company=user.company, name=params.get("employer_name", ""))
    updates = params.get("updates", {})
    employer = update_employer(employer=employer, data=updates)
    return {
        "success": True,
        "message": f"Updated employer '{employer.name}'.",
        "data": {"id": str(employer.id), "name": employer.name},
        "action": "update_employer",
    }


def handle_delete_employer(*, user, params):
    from apps.vacancies.services import delete_employer

    employer = resolve_employer(company=user.company, name=params.get("employer_name", ""))
    name = employer.name
    delete_employer(employer=employer)
    return {
        "success": True,
        "message": f"Deleted employer '{name}'.",
        "data": {},
        "action": "delete_employer",
    }
