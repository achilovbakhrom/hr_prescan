from apps.applications.models import Application


def get_session_score(obj: Application, session_type: str) -> float | None:
    sessions = getattr(obj, "_prefetched_objects_cache", {}).get("sessions")
    if sessions is not None:
        for session in sessions:
            is_completed = session.session_type == session_type and session.status == "completed"
            if is_completed and session.overall_score is not None:
                return float(session.overall_score)
        return None

    from apps.interviews.models import Interview

    session = Interview.objects.filter(application=obj, session_type=session_type, status="completed").first()
    return float(session.overall_score) if session and session.overall_score is not None else None


def get_session_token(obj: Application, session_type: str) -> str | None:
    session = obj.sessions.filter(session_type=session_type).exclude(status="cancelled").order_by("-created_at").first()
    return str(session.interview_token) if session else None
