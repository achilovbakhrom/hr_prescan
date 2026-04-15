"""Handlers for team management, general, and frontend action operations."""

from apps.common.exceptions import ApplicationError


def handle_invite_hr(*, user, params):
    from apps.accounts.services import invite_hr

    email = params.get("email", "")
    invitation = invite_hr(company=user.company, email=email, invited_by=user)
    return {
        "success": True,
        "message": f"Invitation sent to {email}.",
        "data": {"id": str(invitation.id), "email": email},
        "action": "invite_hr",
    }


def handle_list_team(*, user, params):
    from apps.accounts.selectors import get_company_users

    users = get_company_users(company=user.company)
    data = [
        {
            "id": str(u.id),
            "email": u.email,
            "name": f"{u.first_name} {u.last_name}".strip(),
            "role": u.role,
            "is_active": u.is_active,
        }
        for u in users[:50]
    ]
    return {
        "success": True,
        "message": f"Found {len(data)} team member{'s' if len(data) != 1 else ''}.",
        "data": data,
        "action": "list_team",
    }


def handle_toggle_user_active(*, user, params):
    from apps.accounts.models import User
    from apps.accounts.services import activate_user, deactivate_user

    email = params.get("email", "")
    target_user = User.objects.filter(
        company=user.company,
        email__iexact=email,
    ).first()
    if target_user is None:
        raise ApplicationError(f"User with email '{email}' not found in your team.")

    activate = params.get("activate", True)
    if activate:
        target_user = activate_user(user=target_user, activated_by=user)
        return {
            "success": True,
            "message": f"Activated user {email}.",
            "data": {"email": email, "is_active": True},
            "action": "toggle_user_active",
        }
    else:
        target_user = deactivate_user(user=target_user, deactivated_by=user)
        return {
            "success": True,
            "message": f"Deactivated user {email}.",
            "data": {"email": email, "is_active": False},
            "action": "toggle_user_active",
        }


def handle_help(*, user, params):
    help_text = (
        "I can help you with:\n"
        "- **Vacancies**: list, create, update, publish, pause, archive, delete, "
        "generate questions, regenerate keywords\n"
        "- **Employers**: list, create (manual or from URL), update, delete\n"
        "- **Candidates**: list by vacancy, update status, bulk move, add notes\n"
        "- **Interviews**: list, cancel, reset\n"
        "- **Dashboard**: view stats, vacancy summaries\n"
        "- **Subscription**: view plan info, usage stats\n"
        "- **Team**: invite HR, list members, activate/deactivate users\n\n"
        "Just describe what you need in natural language!"
    )
    return {
        "success": True,
        "message": help_text,
        "data": {},
        "action": "help",
    }


def handle_clarify(*, user, params):
    question = params.get("question", "Could you please clarify what you meant?")
    return {
        "success": True,
        "message": question,
        "data": {},
        "action": "clarify",
    }


def handle_error(*, user, params):
    explanation = params.get("explanation", "I could not understand that request.")
    return {
        "success": False,
        "message": explanation,
        "data": {},
        "action": "error",
    }


def handle_unknown(*, user, params):
    return {
        "success": False,
        "message": "I didn't understand that command. Type 'help' to see what I can do.",
        "data": {},
        "action": "unknown",
    }


# ---------------------------------------------------------------------------
# Frontend action handlers
# ---------------------------------------------------------------------------

PAGE_ROUTES = {
    "dashboard": "/dashboard",
    "vacancies": "/vacancies",
    "vacancy-detail": "/vacancies/{id}",
    "employers": "/employers",
    "employer-create": "/employers/create",
    "candidates": "/candidates",
    "interviews": "/interviews",
    "settings": "/settings",
    "profile": "/settings/profile",
    "company-profile": "/settings/company",
    "team": "/settings/team",
    "pricing": "/pricing",
    "subscription": "/subscription",
    "notifications": "/notifications",
    "jobs": "/jobs",
}


def handle_navigate_to_page(*, user, params):
    page = params.get("page", "dashboard")
    route_params = params.get("params", {})

    path = PAGE_ROUTES.get(page, "/dashboard")
    if "{id}" in path and route_params.get("id"):
        path = path.replace("{id}", str(route_params["id"]))

    return {
        "success": True,
        "message": f"Navigating to {page}.",
        "data": {},
        "frontend_action": {"type": "navigate", "path": path},
    }


def handle_clear_chat_history(*, user, params):
    return {
        "success": True,
        "message": "Chat history cleared.",
        "data": {},
        "frontend_action": {"type": "clear_history"},
    }
