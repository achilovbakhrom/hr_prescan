CANDIDATE_PAGE_ROUTES = {
    "dashboard": "/dashboard",
    "jobs": "/jobs",
    "my-applications": "/my-applications",
    "cv-builder": "/cv-builder",
    "profile": "/profile",
}


def _handle_candidate_navigate_to_page(*, user, params):
    page = params.get("page", "dashboard")
    path = CANDIDATE_PAGE_ROUTES.get(page, "/dashboard")

    return {
        "success": True,
        "message": f"Navigating to {page}.",
        "data": {},
        "frontend_action": {"type": "navigate", "path": path},
    }


def _handle_candidate_clear_chat_history(*, user, params):
    return {
        "success": True,
        "message": "Chat history cleared.",
        "data": {},
        "frontend_action": {"type": "clear_history"},
    }
