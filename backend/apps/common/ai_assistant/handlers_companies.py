"""AI assistant handlers for per-user Company CRUD operations."""

from apps.common.ai_assistant.resolvers import resolve_company
from apps.common.country_display import resolve_country_display_name


def handle_list_companies(*, user, params):
    memberships = (
        user.memberships.filter(company__is_deleted=False)
        .select_related("company")
        .order_by("-is_default", "company__created_at")
    )
    data = [
        {
            "id": str(m.company.id),
            "name": m.company.name,
            "industry": m.company.custom_industry,
            "country": resolve_country_display_name(m.company.country),
            "website": m.company.website or "",
            "is_default": m.is_default,
            "role": m.role,
        }
        for m in memberships[:20]
    ]
    return {
        "success": True,
        "message": f"You have {len(data)} compan{'ies' if len(data) != 1 else 'y'}.",
        "data": data,
        "action": "list_companies",
    }


def handle_create_company(*, user, params):
    from apps.accounts.services import create_user_company

    name = (params.get("name") or "").strip()
    if not name:
        return {
            "success": False,
            "message": "Company name is required.",
            "action": "clarify",
        }

    company = create_user_company(
        user=user,
        name=name,
        size=params.get("size") or "small",
        country=params.get("country") or "",
        custom_industry=params.get("industry") or "",
        website=params.get("website") or "",
        description=params.get("description") or "",
    )
    return {
        "success": True,
        "message": f"Created company '{company.name}'.",
        "data": {"id": str(company.id), "name": company.name},
        "action": "create_company",
    }


def handle_update_company(*, user, params):
    from apps.accounts.services import update_user_company

    company = resolve_company(user=user, name=params.get("company_name", ""))
    updates = params.get("updates", {})
    company = update_user_company(user=user, company=company, data=updates)
    return {
        "success": True,
        "message": f"Updated company '{company.name}'.",
        "data": {"id": str(company.id), "name": company.name},
        "action": "update_company",
    }


def handle_delete_company(*, user, params):
    from apps.accounts.services import soft_delete_company

    company = resolve_company(user=user, name=params.get("company_name", ""))
    name = company.name
    soft_delete_company(user=user, company=company)
    return {
        "success": True,
        "message": f"Deleted company '{name}'.",
        "data": {},
        "action": "delete_company",
    }


def handle_set_default_company(*, user, params):
    from apps.accounts.services import set_default_company

    company = resolve_company(user=user, name=params.get("company_name", ""))
    set_default_company(user=user, company_id=company.id)
    return {
        "success": True,
        "message": f"'{company.name}' is now your default company.",
        "data": {"id": str(company.id), "name": company.name},
        "action": "set_default_company",
    }
