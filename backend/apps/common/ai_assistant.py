import json
import logging

from openai import OpenAI

from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI assistant for PreScreen AI, an HR platform.
You help HR managers manage vacancies, candidates, interviews, employers, and team members.
Use the available tools to fulfill requests. You can call multiple tools in sequence to complete complex tasks.
When looking up vacancies or employers by name, use the search/list tools first if needed.
Always confirm what you did in your final response.
If the user's request is ambiguous, ask for clarification instead of guessing.
Respond in the same language the user writes in (English or Russian).
"""

# ---------------------------------------------------------------------------
# OpenAI Tool Definitions
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    # --- Vacancies ---
    {"type": "function", "function": {"name": "list_vacancies", "description": "List company vacancies, optionally filtered by status", "parameters": {"type": "object", "properties": {"status": {"type": "string", "enum": ["draft", "published", "paused", "archived"], "description": "Filter by vacancy status"}}}}},
    {"type": "function", "function": {"name": "create_vacancy", "description": "Create a new job vacancy", "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "Job title"}, "description": {"type": "string", "description": "Job description"}, "employer_name": {"type": "string", "description": "Employer company name to attach"}, "salary_min": {"type": "number"}, "salary_max": {"type": "number"}, "salary_currency": {"type": "string", "default": "USD"}, "location": {"type": "string"}, "is_remote": {"type": "boolean"}, "employment_type": {"type": "string", "enum": ["full_time", "part_time", "contract", "internship"]}, "experience_level": {"type": "string", "enum": ["junior", "middle", "senior", "lead", "director"]}, "skills": {"type": "array", "items": {"type": "string"}}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "update_vacancy", "description": "Update an existing vacancy's fields", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string", "description": "Title of vacancy to update"}, "updates": {"type": "object", "description": "Fields to update: title, description, salary_min, salary_max, location, etc."}}, "required": ["vacancy_title", "updates"]}}},
    {"type": "function", "function": {"name": "publish_vacancy", "description": "Publish a draft or paused vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "pause_vacancy", "description": "Pause a published vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "archive_vacancy", "description": "Archive a published or paused vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "delete_vacancy", "description": "Permanently delete an archived vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "generate_questions", "description": "AI-generate prescanning or interview questions for a vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}, "step": {"type": "string", "enum": ["prescanning", "interview"], "default": "prescanning"}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "regenerate_keywords", "description": "AI-regenerate search keywords for a vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    # --- Employers ---
    {"type": "function", "function": {"name": "list_employers", "description": "List employer companies", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "create_employer", "description": "Create a new employer company", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "industry": {"type": "string"}, "website": {"type": "string"}, "description": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "create_employer_from_url", "description": "Create employer by parsing a website URL with AI", "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "url": {"type": "string"}}, "required": ["name", "url"]}}},
    {"type": "function", "function": {"name": "update_employer", "description": "Update an employer company", "parameters": {"type": "object", "properties": {"employer_name": {"type": "string"}, "updates": {"type": "object"}}, "required": ["employer_name", "updates"]}}},
    {"type": "function", "function": {"name": "delete_employer", "description": "Delete an employer company (only if no vacancies linked)", "parameters": {"type": "object", "properties": {"employer_name": {"type": "string"}}, "required": ["employer_name"]}}},
    # --- Candidates ---
    {"type": "function", "function": {"name": "list_candidates", "description": "List candidates for a vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}, "status": {"type": "string", "enum": ["applied", "prescanned", "interviewed", "shortlisted", "hired", "rejected", "expired", "archived"]}}, "required": ["vacancy_title"]}}},
    {"type": "function", "function": {"name": "update_candidate_status", "description": "Change a candidate's pipeline status", "parameters": {"type": "object", "properties": {"candidate_email_or_name": {"type": "string"}, "vacancy_title": {"type": "string"}, "new_status": {"type": "string", "enum": ["applied", "prescanned", "interviewed", "shortlisted", "hired", "rejected", "archived"]}}, "required": ["candidate_email_or_name", "new_status"]}}},
    {"type": "function", "function": {"name": "bulk_update_status", "description": "Move all candidates from one status to another for a vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}, "from_status": {"type": "string"}, "to_status": {"type": "string"}}, "required": ["vacancy_title", "from_status", "to_status"]}}},
    {"type": "function", "function": {"name": "add_candidate_note", "description": "Add an HR note to a candidate's application", "parameters": {"type": "object", "properties": {"candidate_email_or_name": {"type": "string"}, "vacancy_title": {"type": "string"}, "note": {"type": "string"}}, "required": ["candidate_email_or_name", "note"]}}},
    # --- Interviews ---
    {"type": "function", "function": {"name": "list_interviews", "description": "List interviews, optionally filtered by status", "parameters": {"type": "object", "properties": {"status": {"type": "string", "enum": ["pending", "in_progress", "completed", "cancelled", "expired"]}}}}},
    {"type": "function", "function": {"name": "cancel_interview", "description": "Cancel a pending or in-progress interview", "parameters": {"type": "object", "properties": {"candidate_email_or_name": {"type": "string"}}, "required": ["candidate_email_or_name"]}}},
    {"type": "function", "function": {"name": "reset_interview", "description": "Reset an abandoned interview (creates a new session)", "parameters": {"type": "object", "properties": {"candidate_email_or_name": {"type": "string"}}, "required": ["candidate_email_or_name"]}}},
    # --- Dashboard ---
    {"type": "function", "function": {"name": "get_dashboard", "description": "Get dashboard statistics (active vacancies, candidates, interviews)", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_vacancy_summary", "description": "Get detailed pipeline summary for a specific vacancy", "parameters": {"type": "object", "properties": {"vacancy_title": {"type": "string"}}, "required": ["vacancy_title"]}}},
    # --- Subscription ---
    {"type": "function", "function": {"name": "get_subscription_info", "description": "Get current subscription plan info", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_usage", "description": "Get current usage stats (vacancies, interviews, storage)", "parameters": {"type": "object", "properties": {}}}},
    # --- Team ---
    {"type": "function", "function": {"name": "invite_hr", "description": "Invite a new HR manager to the team", "parameters": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}}},
    {"type": "function", "function": {"name": "list_team", "description": "List team members", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "toggle_user_active", "description": "Activate or deactivate a team member", "parameters": {"type": "object", "properties": {"email": {"type": "string"}, "activate": {"type": "boolean"}}, "required": ["email", "activate"]}}},
]

# ---------------------------------------------------------------------------
# Tool executor — maps tool names to handler functions
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "list_vacancies": "_handle_list_vacancies",
    "create_vacancy": "_handle_create_vacancy",
    "update_vacancy": "_handle_update_vacancy",
    "publish_vacancy": "_handle_publish_vacancy",
    "pause_vacancy": "_handle_pause_vacancy",
    "archive_vacancy": "_handle_archive_vacancy",
    "delete_vacancy": "_handle_delete_vacancy",
    "generate_questions": "_handle_generate_questions",
    "regenerate_keywords": "_handle_regenerate_keywords",
    "list_employers": "_handle_list_employers",
    "create_employer": "_handle_create_employer",
    "create_employer_from_url": "_handle_create_employer_from_url",
    "update_employer": "_handle_update_employer",
    "delete_employer": "_handle_delete_employer",
    "list_candidates": "_handle_list_candidates",
    "update_candidate_status": "_handle_update_candidate_status",
    "bulk_update_status": "_handle_bulk_update_status",
    "add_candidate_note": "_handle_add_candidate_note",
    "list_interviews": "_handle_list_interviews",
    "cancel_interview": "_handle_cancel_interview",
    "reset_interview": "_handle_reset_interview",
    "get_dashboard": "_handle_get_dashboard",
    "get_vacancy_summary": "_handle_get_vacancy_summary",
    "get_subscription_info": "_handle_get_subscription_info",
    "get_usage": "_handle_get_usage",
    "invite_hr": "_handle_invite_hr",
    "list_team": "_handle_list_team",
    "toggle_user_active": "_handle_toggle_user_active",
}


def _execute_tool(*, user, name, args):
    """Execute a tool call and return result dict."""
    handler_name = TOOL_MAP.get(name)
    if not handler_name:
        return {"error": f"Unknown tool: {name}"}

    handler = globals()[handler_name]
    try:
        return handler(user=user, params=args)
    except ApplicationError as e:
        return {"error": str(e.message)}
    except Exception as e:
        logger.error("AI tool %s error: %s", name, e)
        return {"error": str(e)}


def process_ai_command(*, user, message, context=None):
    """Process a natural language command using agentic tool-calling loop.

    GPT can call multiple tools in sequence to fulfill complex requests like:
    "Create a Python Developer vacancy at TechCorp, publish it, and generate questions"
    """
    client = OpenAI()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if context:
        messages.append({"role": "system", "content": f"Current page context: {json.dumps(context)}"})
    messages.append({"role": "user", "content": message})

    actions_taken = []
    max_iterations = 10

    try:
        for _ in range(max_iterations):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.1,
            )

            msg = response.choices[0].message
            messages.append(msg)

            # If GPT wants to call tools
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    logger.info("AI assistant tool call: %s(%s)", fn_name, fn_args)
                    result = _execute_tool(user=user, name=fn_name, args=fn_args)
                    actions_taken.append({"tool": fn_name, "result": result})

                    # Feed result back to GPT
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str),
                    })
            else:
                # GPT is done — return final text response
                return {
                    "success": True,
                    "message": msg.content or "Done.",
                    "actions": actions_taken,
                }

        # Safety: max iterations reached
        return {
            "success": True,
            "message": "Completed (reached step limit).",
            "actions": actions_taken,
        }

    except Exception as e:
        logger.error("AI assistant error: %s", e)
        return {
            "success": False,
            "message": f"AI service error: {str(e)}",
            "actions": actions_taken,
        }


# ---------------------------------------------------------------------------
# Helper: resolve vacancy by title (fuzzy) scoped to company
# ---------------------------------------------------------------------------

def _resolve_vacancy(*, company, title):
    """Find a vacancy by fuzzy title match within the company."""
    from apps.vacancies.models import Vacancy

    vacancy = (
        Vacancy.objects
        .filter(company=company, is_deleted=False, title__icontains=title)
        .first()
    )
    if vacancy is None:
        raise ApplicationError(f"Vacancy matching '{title}' not found.")
    return vacancy


def _resolve_employer(*, company, name):
    """Find an employer by fuzzy name match within the company."""
    from apps.vacancies.models import EmployerCompany

    employer = (
        EmployerCompany.objects
        .filter(company=company, name__icontains=name)
        .first()
    )
    if employer is None:
        raise ApplicationError(f"Employer matching '{name}' not found.")
    return employer


def _resolve_application(*, company, candidate_email_or_name, vacancy_title=None):
    """Find an application by candidate email or name, optionally scoped to a vacancy."""
    from apps.applications.models import Application
    from django.db.models import Q

    qs = Application.objects.filter(
        vacancy__company=company,
        is_deleted=False,
    ).select_related("vacancy")

    if vacancy_title:
        qs = qs.filter(vacancy__title__icontains=vacancy_title)

    # Try email match first, then name
    app = qs.filter(candidate_email__icontains=candidate_email_or_name).first()
    if app is None:
        app = qs.filter(candidate_name__icontains=candidate_email_or_name).first()
    if app is None:
        raise ApplicationError(f"Candidate matching '{candidate_email_or_name}' not found.")
    return app


def _resolve_interview_for_candidate(*, company, candidate_email_or_name):
    """Find the most recent active interview for a candidate."""
    from apps.interviews.models import Interview
    from django.db.models import Q

    qs = Interview.objects.filter(
        application__vacancy__company=company,
        application__is_deleted=False,
    ).select_related("application", "application__vacancy").order_by("-created_at")

    interview = qs.filter(
        Q(application__candidate_email__icontains=candidate_email_or_name)
        | Q(application__candidate_name__icontains=candidate_email_or_name)
    ).first()
    if interview is None:
        raise ApplicationError(f"No interview found for candidate matching '{candidate_email_or_name}'.")
    return interview


# ---------------------------------------------------------------------------
# VACANCY HANDLERS
# ---------------------------------------------------------------------------

def _handle_list_vacancies(*, user, params):
    from apps.vacancies.selectors import get_company_vacancies

    vacancies = get_company_vacancies(company=user.company, status=params.get("status"))
    data = [
        {
            "id": str(v.id),
            "title": v.title,
            "status": v.status,
            "candidates_total": getattr(v, "candidates_total", None),
        }
        for v in vacancies[:20]
    ]
    return {
        "success": True,
        "message": f"Found {len(data)} vacanc{'y' if len(data) == 1 else 'ies'}.",
        "data": data,
        "action": "list_vacancies",
    }


def _handle_create_vacancy(*, user, params):
    from apps.vacancies.models import EmployerCompany
    from apps.vacancies.services import create_vacancy

    employer = None
    if params.get("employer_name"):
        employer = EmployerCompany.objects.filter(
            company=user.company, name__icontains=params["employer_name"]
        ).first()
        if not employer:
            employer = EmployerCompany.objects.create(
                company=user.company, name=params["employer_name"]
            )

    kwargs = {}
    for field in (
        "salary_min", "salary_max", "salary_currency",
        "location", "is_remote", "employment_type", "experience_level", "skills",
    ):
        if params.get(field) is not None:
            kwargs[field] = params[field]
    if employer:
        kwargs["employer"] = employer

    vacancy = create_vacancy(
        company=user.company,
        created_by=user,
        title=params.get("title", "Untitled"),
        description=params.get("description", ""),
        **kwargs,
    )
    return {
        "success": True,
        "message": f"Created vacancy '{vacancy.title}'.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "create_vacancy",
    }


def _handle_update_vacancy(*, user, params):
    from apps.vacancies.services import update_vacancy

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    updates = params.get("updates", {})
    vacancy = update_vacancy(vacancy=vacancy, data=updates)
    return {
        "success": True,
        "message": f"Updated vacancy '{vacancy.title}'.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "update_vacancy",
    }


def _handle_publish_vacancy(*, user, params):
    from apps.vacancies.services import publish_vacancy

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = publish_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' is now published.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "publish_vacancy",
    }


def _handle_pause_vacancy(*, user, params):
    from apps.vacancies.services import pause_vacancy

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = pause_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' is now paused.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "pause_vacancy",
    }


def _handle_archive_vacancy(*, user, params):
    from apps.vacancies.services import archive_vacancy

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    vacancy = archive_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' has been archived.",
        "data": {"id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status},
        "action": "archive_vacancy",
    }


def _handle_delete_vacancy(*, user, params):
    from apps.vacancies.services import soft_delete_vacancy

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    soft_delete_vacancy(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Vacancy '{vacancy.title}' has been deleted.",
        "data": {"id": str(vacancy.id), "title": vacancy.title},
        "action": "delete_vacancy",
    }


def _handle_generate_questions(*, user, params):
    from apps.vacancies.services import generate_interview_questions

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    step = params.get("step", "prescanning")
    questions = generate_interview_questions(vacancy=vacancy, step=step)
    data = [{"text": q.text, "category": q.category} for q in questions]
    return {
        "success": True,
        "message": f"Generated {len(data)} {step} questions for '{vacancy.title}'.",
        "data": data,
        "action": "generate_questions",
    }


def _handle_regenerate_keywords(*, user, params):
    from apps.vacancies.services import generate_vacancy_keywords

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    keywords = generate_vacancy_keywords(vacancy=vacancy)
    return {
        "success": True,
        "message": f"Regenerated {len(keywords)} keywords for '{vacancy.title}'.",
        "data": {"keywords": keywords},
        "action": "regenerate_keywords",
    }


# ---------------------------------------------------------------------------
# EMPLOYER HANDLERS
# ---------------------------------------------------------------------------

def _handle_list_employers(*, user, params):
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


def _handle_create_employer(*, user, params):
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


def _handle_create_employer_from_url(*, user, params):
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


def _handle_update_employer(*, user, params):
    from apps.vacancies.services import update_employer

    employer = _resolve_employer(company=user.company, name=params.get("employer_name", ""))
    updates = params.get("updates", {})
    employer = update_employer(employer=employer, data=updates)
    return {
        "success": True,
        "message": f"Updated employer '{employer.name}'.",
        "data": {"id": str(employer.id), "name": employer.name},
        "action": "update_employer",
    }


def _handle_delete_employer(*, user, params):
    from apps.vacancies.services import delete_employer

    employer = _resolve_employer(company=user.company, name=params.get("employer_name", ""))
    name = employer.name
    delete_employer(employer=employer)
    return {
        "success": True,
        "message": f"Deleted employer '{name}'.",
        "data": {},
        "action": "delete_employer",
    }


# ---------------------------------------------------------------------------
# CANDIDATE HANDLERS
# ---------------------------------------------------------------------------

def _handle_list_candidates(*, user, params):
    from apps.applications.selectors import get_vacancy_applications

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
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


def _handle_update_candidate_status(*, user, params):
    from apps.applications.services import update_application_status

    application = _resolve_application(
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


def _handle_bulk_update_status(*, user, params):
    from apps.applications.services import bulk_move_by_filter

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))
    count = bulk_move_by_filter(
        vacancy_id=vacancy.id,
        from_status=params.get("from_status", ""),
        to_status=params.get("to_status", ""),
        updated_by=user,
    )
    return {
        "success": True,
        "message": f"Moved {count} candidate{'s' if count != 1 else ''} from '{params.get('from_status')}' to '{params.get('to_status')}'.",
        "data": {"count": count},
        "action": "bulk_update_status",
    }


def _handle_add_candidate_note(*, user, params):
    from apps.applications.services import add_hr_note

    application = _resolve_application(
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


# ---------------------------------------------------------------------------
# INTERVIEW HANDLERS
# ---------------------------------------------------------------------------

def _handle_list_interviews(*, user, params):
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


def _handle_cancel_interview(*, user, params):
    from apps.interviews.services import cancel_interview

    interview = _resolve_interview_for_candidate(
        company=user.company,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
    )
    interview = cancel_interview(interview=interview)
    return {
        "success": True,
        "message": f"Cancelled interview for {interview.application.candidate_name}.",
        "data": {"id": str(interview.id), "status": interview.status},
        "action": "cancel_interview",
    }


def _handle_reset_interview(*, user, params):
    from apps.interviews.services import reset_interview

    interview = _resolve_interview_for_candidate(
        company=user.company,
        candidate_email_or_name=params.get("candidate_email_or_name", ""),
    )
    new_interview = reset_interview(interview=interview)
    return {
        "success": True,
        "message": f"Reset interview for {interview.application.candidate_name}. A new session has been created.",
        "data": {"id": str(new_interview.id), "status": new_interview.status},
        "action": "reset_interview",
    }


# ---------------------------------------------------------------------------
# DASHBOARD HANDLERS
# ---------------------------------------------------------------------------

def _handle_get_dashboard(*, user, params):
    from apps.common.selectors import get_dashboard_stats

    stats = get_dashboard_stats(company=user.company)
    return {
        "success": True,
        "message": "Here are your dashboard stats.",
        "data": stats,
        "action": "get_dashboard",
    }


def _handle_get_vacancy_summary(*, user, params):
    from apps.applications.models import Application
    from apps.interviews.models import Interview

    vacancy = _resolve_vacancy(company=user.company, title=params.get("vacancy_title", ""))

    total_candidates = Application.objects.filter(
        vacancy=vacancy, is_deleted=False,
    ).count()
    by_status = {}
    for s in Application.Status:
        count = Application.objects.filter(
            vacancy=vacancy, is_deleted=False, status=s.value,
        ).count()
        if count > 0:
            by_status[s.value] = count

    pending_interviews = Interview.objects.filter(
        application__vacancy=vacancy,
        status=Interview.Status.PENDING,
    ).count()
    completed_interviews = Interview.objects.filter(
        application__vacancy=vacancy,
        status=Interview.Status.COMPLETED,
    ).count()

    data = {
        "id": str(vacancy.id),
        "title": vacancy.title,
        "status": vacancy.status,
        "total_candidates": total_candidates,
        "candidates_by_status": by_status,
        "pending_interviews": pending_interviews,
        "completed_interviews": completed_interviews,
    }
    return {
        "success": True,
        "message": f"Summary for '{vacancy.title}'.",
        "data": data,
        "action": "get_vacancy_summary",
    }


# ---------------------------------------------------------------------------
# SUBSCRIPTION HANDLERS
# ---------------------------------------------------------------------------

def _handle_get_subscription_info(*, user, params):
    from apps.subscriptions.selectors import get_company_subscription

    subscription = get_company_subscription(company=user.company)
    if subscription is None:
        return {
            "success": True,
            "message": "No active subscription found.",
            "data": {"has_subscription": False},
            "action": "get_subscription_info",
        }
    data = {
        "has_subscription": True,
        "plan": subscription.plan.name,
        "tier": subscription.plan.tier,
        "billing_period": subscription.billing_period,
        "is_active": subscription.is_active,
        "current_period_end": subscription.current_period_end.isoformat(),
    }
    return {
        "success": True,
        "message": f"You are on the {subscription.plan.name} plan.",
        "data": data,
        "action": "get_subscription_info",
    }


def _handle_get_usage(*, user, params):
    from apps.subscriptions.services import get_subscription_usage

    usage = get_subscription_usage(company=user.company)
    return {
        "success": True,
        "message": "Here is your current usage.",
        "data": usage,
        "action": "get_usage",
    }


# ---------------------------------------------------------------------------
# TEAM HANDLERS
# ---------------------------------------------------------------------------

def _handle_invite_hr(*, user, params):
    from apps.accounts.services import invite_hr

    email = params.get("email", "")
    invitation = invite_hr(company=user.company, email=email, invited_by=user)
    return {
        "success": True,
        "message": f"Invitation sent to {email}.",
        "data": {"id": str(invitation.id), "email": email},
        "action": "invite_hr",
    }


def _handle_list_team(*, user, params):
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


def _handle_toggle_user_active(*, user, params):
    from apps.accounts.models import User
    from apps.accounts.services import activate_user, deactivate_user

    email = params.get("email", "")
    target_user = User.objects.filter(
        company=user.company, email__iexact=email,
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


# ---------------------------------------------------------------------------
# GENERAL HANDLERS
# ---------------------------------------------------------------------------

def _handle_help(*, user, params):
    help_text = (
        "I can help you with:\n"
        "- **Vacancies**: list, create, update, publish, pause, archive, delete, generate questions, regenerate keywords\n"
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


def _handle_clarify(*, user, params):
    question = params.get("question", "Could you please clarify what you meant?")
    return {
        "success": True,
        "message": question,
        "data": {},
        "action": "clarify",
    }


def _handle_error(*, user, params):
    explanation = params.get("explanation", "I could not understand that request.")
    return {
        "success": False,
        "message": explanation,
        "data": {},
        "action": "error",
    }


def _handle_unknown(*, user, params):
    return {
        "success": False,
        "message": "I didn't understand that command. Type 'help' to see what I can do.",
        "data": {},
        "action": "unknown",
    }


