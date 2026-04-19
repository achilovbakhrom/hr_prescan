"""Helpers for the AI vacancy-creation flow that pick which company a new vacancy goes under."""

from apps.accounts.models import Company


def user_live_companies(user):
    return Company.objects.filter(
        id__in=user.memberships.values_list("company_id", flat=True),
        is_deleted=False,
    )


def resolve_company_for_create(*, user, params):
    """Pick a company for a new vacancy.

    Returns ``(company, clarify_response_or_None)``. When the second element is not ``None``,
    the caller returns it directly — the LLM must ask the user which company before proceeding.
    """
    companies = user_live_companies(user)
    count = companies.count()

    if count == 0:
        return None, {
            "success": False,
            "message": "You don't have any companies yet. Create a company first.",
            "action": "clarify",
        }

    if count == 1:
        return companies.first(), None

    company_name = (params.get("company_name") or "").strip()
    garbage = {"not provided", "not specified", "unknown", "n/a", "none"}
    if company_name and company_name.lower() not in garbage:
        match = companies.filter(name__icontains=company_name).first()
        if match is not None:
            return match, None
        names = ", ".join(companies.values_list("name", flat=True))
        return None, {
            "success": False,
            "message": (
                f"I couldn't find a company matching '{company_name}'. Your companies are: {names}. Which one?"
            ),
            "action": "clarify",
        }

    if params.get("use_default"):
        default = user.memberships.filter(is_default=True, company__is_deleted=False).select_related("company").first()
        if default is not None:
            return default.company, None

    names = ", ".join(companies.values_list("name", flat=True))
    return None, {
        "success": False,
        "message": (
            f"You have {count} companies: {names}. "
            "Which one should this vacancy be under? (Or say 'use default' to use your default.)"
        ),
        "action": "clarify",
    }
