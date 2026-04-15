"""Handlers for candidate/application-related AI assistant operations."""

from apps.common.ai_assistant.resolvers import resolve_application, resolve_vacancy


def handle_list_candidates(*, user, params):
    from apps.applications.selectors import get_vacancy_applications

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    applications = get_vacancy_applications(vacancy=vacancy, status=params.get("status"))
    data = [
        {
            "id": str(a.id),
            "name": a.candidate_name,
            "email": a.candidate_email,
            "status": a.status,
            "match_score": float(a.match_score) if a.match_score is not None else None,
        }
        for a in applications[:20]
    ]
    return {
        "success": True,
        "message": f"Found {len(data)} candidate{'s' if len(data) != 1 else ''} for '{vacancy.title}'.",
        "data": data,
        "action": "list_candidates",
    }


def handle_update_candidate_status(*, user, params):
    from apps.applications.services import update_application_status

    application = resolve_application(
        company=user.company,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
        vacancy_title=params.get("vacancy_title"),
    )
    application = update_application_status(
        application=application,
        status=params.get("new_status", ""),
        updated_by=user,
    )
    return {
        "success": True,
        "message": f"Updated {application.candidate_name}'s status to '{application.status}'.",
        "data": {
            "id": str(application.id),
            "name": application.candidate_name,
            "status": application.status,
        },
        "action": "update_candidate_status",
    }


def handle_bulk_update_status(*, user, params):
    from apps.applications.services import bulk_move_by_filter

    vacancy = resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    count = bulk_move_by_filter(
        vacancy_id=vacancy.id,
        from_status=params.get("from_status", ""),
        to_status=params.get("to_status", ""),
        updated_by=user,
    )
    return {
        "success": True,
        "message": (
            f"Moved {count} candidate{'s' if count != 1 else ''} "
            f"from '{params.get('from_status')}' to '{params.get('to_status')}'."
        ),
        "data": {"count": count},
        "action": "bulk_update_status",
    }


def handle_add_candidate_note(*, user, params):
    from apps.applications.services import add_hr_note

    application = resolve_application(
        company=user.company,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
        vacancy_title=params.get("vacancy_title"),
    )
    application = add_hr_note(
        application=application,
        note=params.get("note", ""),
    )
    return {
        "success": True,
        "message": f"Added note to {application.candidate_name}'s application.",
        "data": {"id": str(application.id), "name": application.candidate_name},
        "action": "add_candidate_note",
    }
