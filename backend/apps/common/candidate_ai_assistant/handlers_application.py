from apps.common.exceptions import ApplicationError


def _handle_list_my_applications(*, user, params):
    from apps.applications.models import Application

    applications = (
        Application.objects
        .filter(candidate=user, is_deleted=False)
        .select_related("vacancy", "vacancy__company", "vacancy__employer")
        .order_by("-created_at")
    )

    total = applications.count()
    data = [
        {
            "id": str(a.id),
            "vacancy_title": a.vacancy.title,
            "company": a.vacancy.company.name if a.vacancy.company else "",
            "employer": a.vacancy.employer.name if a.vacancy.employer else "",
            "status": a.status,
            "match_score": float(a.match_score) if a.match_score is not None else None,
            "applied_at": a.created_at.isoformat(),
        }
        for a in applications[:20]
    ]

    msg = f"You have {total} application{'s' if total != 1 else ''}."
    if total == 0:
        msg = "You haven't applied to any jobs yet. Would you like me to search for jobs?"
    elif total > 20:
        msg += " Showing the 20 most recent."

    return {
        "success": True,
        "message": msg,
        "data": data,
        "action": "list_my_applications",
    }


def _handle_get_application_details(*, user, params):
    from apps.applications.models import Application

    application_id = params.get("application_id", "")
    try:
        application = (
            Application.objects
            .select_related("vacancy", "vacancy__company", "vacancy__employer")
            .get(id=application_id, candidate=user, is_deleted=False)
        )
    except (Application.DoesNotExist, ValueError):
        raise ApplicationError("Application not found.") from None

    data = {
        "id": str(application.id),
        "vacancy_title": application.vacancy.title,
        "company": application.vacancy.company.name if application.vacancy.company else "",
        "employer": application.vacancy.employer.name if application.vacancy.employer else "",
        "status": application.status,
        "match_score": float(application.match_score) if application.match_score is not None else None,
        "applied_at": application.created_at.isoformat(),
        "cv_uploaded": bool(application.cv_file),
    }

    return {
        "success": True,
        "message": f"Details for your application to '{application.vacancy.title}'.",
        "data": data,
        "action": "get_application_details",
    }
