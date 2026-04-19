"""Handlers for interview-related AI assistant operations."""

from apps.common.ai_assistant.resolvers import resolve_interview_for_candidate


def handle_list_interviews(*, user, params):
    from apps.interviews.selectors import get_company_interviews

    interviews = get_company_interviews(company=user.company, status=params.get("status"))
    data = [
        {
            "id": str(i.id),
            "candidate_name": i.application.candidate_name,
            "vacancy_title": i.application.vacancy.title,
            "session_type": i.session_type,
            "status": i.status,
            "overall_score": float(i.overall_score) if i.overall_score is not None else None,
        }
        for i in interviews[:20]
    ]
    return {
        "success": True,
        "message": f"Found {len(data)} interview{'s' if len(data) != 1 else ''}.",
        "data": data,
        "action": "list_interviews",
    }


def handle_cancel_interview(*, user, params):
    from apps.interviews.services import cancel_interview

    interview = resolve_interview_for_candidate(
        user=user,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
    )
    interview = cancel_interview(interview=interview)
    return {
        "success": True,
        "message": f"Cancelled interview for {interview.application.candidate_name}.",
        "data": {"id": str(interview.id), "status": interview.status},
        "action": "cancel_interview",
    }


def handle_reset_interview(*, user, params):
    from apps.interviews.services import reset_interview

    interview = resolve_interview_for_candidate(
        user=user,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
    )
    new_interview = reset_interview(interview=interview)
    return {
        "success": True,
        "message": f"Reset interview for {interview.application.candidate_name}. A new session has been created.",
        "data": {"id": str(new_interview.id), "status": new_interview.status},
        "action": "reset_interview",
    }
