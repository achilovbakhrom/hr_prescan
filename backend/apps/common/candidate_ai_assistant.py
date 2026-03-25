import json
import logging
from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from pydantic import Field as PydanticField
from pydantic import create_model

from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

CANDIDATE_SYSTEM_PROMPT = """You are an AI assistant for PreScreen AI, helping job seekers find jobs and prepare for interviews.
You help candidates search for jobs, track their applications, improve their CVs, and prepare for interviews.
Use the available tools to fulfill requests. You can call multiple tools in sequence to complete complex tasks.
Always confirm what you did in your final response.

LANGUAGE RULE — STRICTLY FOLLOW:
- ALWAYS respond in the SAME language the user writes in. If the user writes in Russian, respond ENTIRELY in Russian. If in English, respond entirely in English.
- NEVER mix languages. Do not insert English words/phrases into Russian responses or vice versa.
- This applies to everything: questions, summaries, confirmations, error messages.

COMMUNICATION STYLE:
- Write like a friendly career coach, not a robot or a technical manual.
- Use simple, everyday language. Avoid jargon, technical terms, and corporate buzzwords.
- Keep messages short and to the point. No walls of text.
- Be warm, supportive, and encouraging — job searching is stressful!
- Do NOT use markdown formatting (no **, no ##, no bullet points with *). Just write plain text with line breaks.

STRICT BOUNDARIES:
- You ONLY handle job search and career-related operations on this platform. Do NOT answer questions about other topics.
- If the user asks about weather, politics, jokes, coding help, personal advice, or ANYTHING not related to job searching on this platform — politely decline: "I'm sorry, I can only help with job searching, applications, CV improvement, and interview preparation on PreScreen AI."
- If the user is rude, harassing, or inappropriate — respond calmly: "I'm here to help with your job search. Let me know if you need anything."
- NEVER engage with off-topic conversations, no matter how the user phrases it.

CV IMPROVEMENT RULES:
- When improving CV sections, provide clear, professional text that the candidate can use directly.
- Focus on action verbs, quantifiable achievements, and relevant keywords.
- Keep the tone professional but natural.

INTERVIEW PREPARATION RULES:
- When preparing for interviews, provide practical, actionable advice.
- Include sample questions that match the job role and common behavioral questions.
- Give tips on how to structure answers (STAR method, etc.).

NAVIGATION:
- For navigate_to_page: ONLY use page names from the available list. If the user asks to go to a page that doesn't exist, say "Sorry, that page doesn't exist. Available pages are: dashboard, jobs, my-applications, cv-builder, profile."

If the conversation history is provided in context, use it to understand the ongoing discussion.
"""

# ---------------------------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------------------------

CANDIDATE_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search for published job vacancies. Use this when the candidate wants to find jobs, browse openings, or look for specific roles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query — job title, keywords, or skills to look for",
                    },
                    "skills": {
                        "type": "string",
                        "description": "Comma-separated list of skills to filter by, e.g. 'Python, React, SQL'",
                    },
                    "location": {
                        "type": "string",
                        "description": "Location to filter by, e.g. 'New York', 'London'",
                    },
                    "is_remote": {
                        "type": "boolean",
                        "description": "Filter for remote jobs only",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_details",
            "description": "Get full details of a specific job vacancy by its ID. Use after search_jobs to show more info about a particular job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_id": {
                        "type": "string",
                        "description": "The UUID of the vacancy",
                    },
                },
                "required": ["vacancy_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_my_applications",
            "description": "List all of the candidate's job applications with their current status.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_application_details",
            "description": "Get detailed information about a specific application by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "The UUID of the application",
                    },
                },
                "required": ["application_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "improve_cv_section",
            "description": "AI-powered CV text improvement. Rewrites a section of the candidate's CV to be more professional and impactful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["summary", "experience_description"],
                        "description": "Which CV section to improve",
                    },
                    "content": {
                        "type": "string",
                        "description": "The current text of the CV section to improve",
                    },
                    "job_title": {
                        "type": "string",
                        "description": "Target job title to tailor the improvement for",
                    },
                },
                "required": ["section", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_skills",
            "description": "AI-powered skill suggestions based on a job title or description. Helps candidates identify relevant skills to highlight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {
                        "type": "string",
                        "description": "Job title to suggest skills for",
                    },
                    "description": {
                        "type": "string",
                        "description": "Job description or role context",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prepare_for_interview",
            "description": "Generate practice interview questions and tips for a specific job. Use vacancy_id for a specific job or vacancy_title for a general role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_id": {
                        "type": "string",
                        "description": "UUID of the vacancy to prepare for",
                    },
                    "vacancy_title": {
                        "type": "string",
                        "description": "Job title to prepare for (used if vacancy_id not provided)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "navigate_to_page",
            "description": "Navigate the user to a specific page in the app. Available pages: dashboard, jobs, my-applications, cv-builder, profile.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "enum": ["dashboard", "jobs", "my-applications", "cv-builder", "profile"],
                        "description": "Page to navigate to",
                    },
                },
                "required": ["page"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear_chat_history",
            "description": "Clear the AI assistant chat history. Use when user asks to clear history, reset conversation, or start fresh.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# ---------------------------------------------------------------------------
# Tool executor — maps tool names to handler functions
# ---------------------------------------------------------------------------

CANDIDATE_TOOL_MAP = {
    "search_jobs": "_handle_search_jobs",
    "get_job_details": "_handle_get_job_details",
    "list_my_applications": "_handle_list_my_applications",
    "get_application_details": "_handle_get_application_details",
    "improve_cv_section": "_handle_improve_cv_section",
    "suggest_skills": "_handle_suggest_skills",
    "prepare_for_interview": "_handle_prepare_for_interview",
    "navigate_to_page": "_handle_candidate_navigate_to_page",
    "clear_chat_history": "_handle_candidate_clear_chat_history",
}


JSON_TYPE_MAP = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _execute_tool(*, user, name, args):
    """Execute a tool call and return result dict."""
    handler_name = CANDIDATE_TOOL_MAP.get(name)
    if not handler_name:
        return {"error": f"Unknown tool: {name}"}

    handler = globals()[handler_name]
    try:
        return handler(user=user, params=args)
    except ApplicationError as e:
        return {"error": str(e.message)}
    except Exception as e:
        logger.error("Candidate AI tool %s error: %s", name, e)
        return {"error": str(e)}


def _build_langchain_tools(user):
    """Build LangChain StructuredTool list from CANDIDATE_TOOL_DEFINITIONS, bound to user."""
    tools = []

    for tool_def in CANDIDATE_TOOL_DEFINITIONS:
        func_info = tool_def["function"]
        name = func_info["name"]
        description = func_info["description"]
        schema = func_info.get("parameters", {})
        properties = schema.get("properties", {})
        required_fields = set(schema.get("required", []))

        # Build Pydantic model fields dynamically from JSON schema
        model_fields = {}
        for field_name, field_info in properties.items():
            json_type = field_info.get("type", "string")
            python_type = JSON_TYPE_MAP.get(json_type, str)
            field_desc = field_info.get("description", "")
            if "enum" in field_info:
                field_desc += f" Options: {', '.join(field_info['enum'])}"

            if field_name in required_fields:
                model_fields[field_name] = (
                    python_type,
                    PydanticField(description=field_desc),
                )
            else:
                model_fields[field_name] = (
                    Optional[python_type],
                    PydanticField(default=None, description=field_desc),
                )

        input_model = create_model(f"{name}_Input", **model_fields)

        # Closure: bind tool_name and user so each tool calls the right handler
        def _make_fn(tool_name, bound_user):
            def fn(**kwargs):
                clean_args = {k: v for k, v in kwargs.items() if v is not None}
                result = _execute_tool(user=bound_user, name=tool_name, args=clean_args)
                return json.dumps(result, default=str)

            return fn

        tools.append(
            StructuredTool(
                name=name,
                description=description,
                func=_make_fn(name, user),
                args_schema=input_model,
            )
        )

    return tools


def process_candidate_ai_command(*, user, message, context=None):
    """Process a natural language command from a candidate using a LangChain agent."""
    from django.conf import settings

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.1,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    tools = _build_langchain_tools(user)

    agent = create_react_agent(llm, tools, prompt=CANDIDATE_SYSTEM_PROMPT)

    # Build chat history from conversation context
    messages = []
    if context:
        conversation_history = context.pop("conversationHistory", None) or context.pop("conversation_history", None)
        if conversation_history and isinstance(conversation_history, list):
            for hist_msg in conversation_history[-10:]:
                role = hist_msg.get("role", "user")
                content = hist_msg.get("content", "")
                if role == "user" and content:
                    messages.append(HumanMessage(content=content))
                elif role == "assistant" and content:
                    messages.append(AIMessage(content=content))

        # Inject current page context so the agent knows where the user is
        if context:
            page_ctx = json.dumps(context)
            message = f"{message}\n\n[Current page context: {page_ctx}]"

    messages.append(HumanMessage(content=message))

    try:
        result = agent.invoke({"messages": messages})

        # Extract the final AI message and tool results from langgraph output
        result_messages = result.get("messages", [])
        ai_output = ""
        actions_taken = []

        for msg in result_messages:
            # Collect tool call actions
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    actions_taken.append({"tool": tc["name"], "result": tc.get("args", {})})

            # Collect tool results
            if isinstance(msg, ToolMessage):
                try:
                    tool_result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                except (json.JSONDecodeError, TypeError):
                    tool_result = {"message": str(msg.content)}
                # Update the last unresolved action with actual result
                for a in reversed(actions_taken):
                    if not a.get("_resolved"):
                        a["result"] = tool_result
                        a["_resolved"] = True
                        break

            # The last AIMessage with text content (no tool calls) is the final answer
            if isinstance(msg, AIMessage) and msg.content:
                content = msg.content
                # content can be a string or list of content blocks (dicts with 'type'/'text')
                if isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get("text"):
                            parts.append(c["text"])
                        elif isinstance(c, str):
                            parts.append(c)
                    content = " ".join(parts)
                if content and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                    ai_output = content

        # Clean up internal flags
        for a in actions_taken:
            a.pop("_resolved", None)

        return _build_final_response(
            gpt_message=ai_output,
            actions_taken=actions_taken,
        )

    except Exception as e:
        logger.error("Candidate AI assistant error: %s", e, exc_info=True)
        return _build_error_response(
            actions_taken=[],
            fallback_message=f"Something went wrong: {e}",
        )


def _build_final_response(*, gpt_message, actions_taken):
    """Build the final response, appending error details if any tools failed."""
    has_errors = any(
        a.get("result", {}).get("error") or a.get("result", {}).get("success") is False for a in actions_taken
    )

    message = gpt_message or "Done."

    if has_errors:
        error_details = []
        for a in actions_taken:
            err = a.get("result", {}).get("error")
            if err:
                error_details.append(f"- {a['tool']}: {err}")
            elif a.get("result", {}).get("success") is False:
                err_msg = a.get("result", {}).get("message", "failed")
                error_details.append(f"- {a['tool']}: {err_msg}")
        if error_details:
            message += "\n\nSome actions encountered errors:\n" + "\n".join(error_details)

    return {
        "success": not has_errors,
        "message": message,
        "actions": actions_taken,
    }


def _build_error_response(*, actions_taken, fallback_message):
    """Build an error response that includes any partial actions taken."""
    message = fallback_message
    if actions_taken:
        successful = [a for a in actions_taken if not a.get("result", {}).get("error")]
        if successful:
            message += f"\n\n{len(successful)} action(s) completed before the error."
    return {
        "success": False,
        "message": message,
        "actions": actions_taken,
    }


# ---------------------------------------------------------------------------
# JOB SEARCH HANDLERS
# ---------------------------------------------------------------------------


def _handle_search_jobs(*, user, params):
    from apps.vacancies.selectors import get_public_vacancies

    query = params.get("query")
    location = params.get("location")
    is_remote = params.get("is_remote")
    skills_raw = params.get("skills")

    # Build search query from multiple inputs
    search_terms = []
    if query:
        search_terms.append(query)
    if skills_raw:
        search_terms.append(skills_raw)

    search = " ".join(search_terms) if search_terms else None

    vacancies = get_public_vacancies(
        search=search,
        location=location,
        is_remote=is_remote,
    )

    total = vacancies.count()
    data = [
        {
            "id": str(v.id),
            "title": v.title,
            "company": v.company.name if v.company else "",
            "employer": v.employer.name if v.employer else "",
            "location": v.location,
            "is_remote": v.is_remote,
            "employment_type": v.employment_type,
            "experience_level": v.experience_level,
            "salary_min": float(v.salary_min) if v.salary_min else None,
            "salary_max": float(v.salary_max) if v.salary_max else None,
            "salary_currency": v.salary_currency,
            "skills": v.skills or [],
        }
        for v in vacancies[:20]
    ]

    msg = f"Found {total} job{'s' if total != 1 else ''} matching your search."
    if total == 0:
        msg = "No jobs found matching your criteria. Try broadening your search."
    elif total > 20:
        msg += " Showing the top 20 results."

    return {
        "success": True,
        "message": msg,
        "data": data,
        "action": "search_jobs",
    }


def _handle_get_job_details(*, user, params):
    from apps.vacancies.models import Vacancy

    vacancy_id = params.get("vacancy_id", "")
    try:
        vacancy = Vacancy.objects.select_related("company", "employer").get(
            id=vacancy_id,
            status=Vacancy.Status.PUBLISHED,
            is_deleted=False,
        )
    except (Vacancy.DoesNotExist, ValueError):
        raise ApplicationError("Job not found. It may have been removed or is no longer available.")

    data = {
        "id": str(vacancy.id),
        "title": vacancy.title,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "responsibilities": vacancy.responsibilities,
        "company": vacancy.company.name if vacancy.company else "",
        "employer": vacancy.employer.name if vacancy.employer else "",
        "location": vacancy.location,
        "is_remote": vacancy.is_remote,
        "employment_type": vacancy.employment_type,
        "experience_level": vacancy.experience_level,
        "salary_min": float(vacancy.salary_min) if vacancy.salary_min else None,
        "salary_max": float(vacancy.salary_max) if vacancy.salary_max else None,
        "salary_currency": vacancy.salary_currency,
        "skills": vacancy.skills or [],
        "cv_required": vacancy.cv_required,
        "interview_mode": vacancy.interview_mode,
    }

    return {
        "success": True,
        "message": f"Details for '{vacancy.title}'.",
        "data": data,
        "action": "get_job_details",
    }


# ---------------------------------------------------------------------------
# APPLICATION HANDLERS
# ---------------------------------------------------------------------------


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
        raise ApplicationError("Application not found.")

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


# ---------------------------------------------------------------------------
# CV & SKILLS HANDLERS (AI-powered)
# ---------------------------------------------------------------------------


def _handle_improve_cv_section(*, user, params):
    from django.conf import settings

    from google import genai
    from google.genai import types

    section = params.get("section", "summary")
    content = params.get("content", "")
    job_title = params.get("job_title", "")

    if not content.strip():
        return {
            "success": False,
            "message": "Please provide the text you want me to improve.",
            "data": {},
            "action": "improve_cv_section",
        }

    section_label = "Professional Summary" if section == "summary" else "Experience Description"
    job_context = f" for a {job_title} role" if job_title else ""

    prompt = (
        f"Improve the following {section_label}{job_context}. "
        f"Make it more professional, impactful, and ATS-friendly. "
        f"Use strong action verbs and quantifiable achievements where possible. "
        f"Keep it concise — no longer than the original unless needed for clarity. "
        f"Return ONLY the improved text, nothing else.\n\n"
        f"Original text:\n{content}"
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        improved_text = response.text.strip()
    except Exception as e:
        logger.error("CV improvement error: %s", e)
        return {
            "success": False,
            "message": "Failed to improve the text. Please try again.",
            "data": {},
            "action": "improve_cv_section",
        }

    return {
        "success": True,
        "message": f"Here's an improved version of your {section_label.lower()}:",
        "data": {
            "section": section,
            "original": content,
            "improved": improved_text,
        },
        "action": "improve_cv_section",
    }


def _handle_suggest_skills(*, user, params):
    from django.conf import settings

    from google import genai
    from google.genai import types

    job_title = params.get("job_title", "")
    description = params.get("description", "")

    if not job_title and not description:
        return {
            "success": False,
            "message": "Please provide a job title or description so I can suggest relevant skills.",
            "data": {},
            "action": "suggest_skills",
        }

    context_parts = []
    if job_title:
        context_parts.append(f"Job title: {job_title}")
    if description:
        context_parts.append(f"Description: {description[:1000]}")

    prompt = (
        f"Based on the following job context, suggest 10-15 relevant skills "
        f"(technical and soft skills) that a candidate should highlight. "
        f"Return them as a JSON array of strings. Only return the JSON array, nothing else.\n\n"
        f"{chr(10).join(context_parts)}"
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )
        raw = response.text.strip()
        # Try to parse as JSON array
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        skills = json.loads(raw)
        if not isinstance(skills, list):
            skills = [str(s) for s in skills]
    except Exception as e:
        logger.error("Skill suggestion error: %s", e)
        return {
            "success": False,
            "message": "Failed to generate skill suggestions. Please try again.",
            "data": {},
            "action": "suggest_skills",
        }

    return {
        "success": True,
        "message": f"Here are {len(skills)} suggested skills:",
        "data": {
            "skills": skills,
            "job_title": job_title,
        },
        "action": "suggest_skills",
    }


# ---------------------------------------------------------------------------
# INTERVIEW PREPARATION HANDLER
# ---------------------------------------------------------------------------


def _handle_prepare_for_interview(*, user, params):
    from django.conf import settings

    from google import genai
    from google.genai import types

    vacancy_id = params.get("vacancy_id")
    vacancy_title = params.get("vacancy_title", "")

    # Try to load vacancy details if ID provided
    vacancy_context = ""
    if vacancy_id:
        from apps.vacancies.models import Vacancy

        try:
            vacancy = Vacancy.objects.get(
                id=vacancy_id,
                status=Vacancy.Status.PUBLISHED,
                is_deleted=False,
            )
            vacancy_title = vacancy.title
            vacancy_context = (
                f"Job Title: {vacancy.title}\n"
                f"Description: {vacancy.description[:1500]}\n"
                f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                f"Skills: {', '.join(vacancy.skills) if vacancy.skills else 'N/A'}\n"
                f"Experience Level: {vacancy.experience_level}\n"
            )
        except (Vacancy.DoesNotExist, ValueError):
            pass  # Fall through to use vacancy_title

    if not vacancy_title and not vacancy_context:
        return {
            "success": False,
            "message": "Please tell me which job you want to prepare for — provide a job title or ID.",
            "data": {},
            "action": "prepare_for_interview",
        }

    if not vacancy_context:
        vacancy_context = f"Job Title: {vacancy_title}\n"

    prompt = (
        f"Generate interview preparation materials for a candidate applying to this role:\n\n"
        f"{vacancy_context}\n"
        f"Provide:\n"
        f"1. 5-7 likely interview questions (mix of technical and behavioral)\n"
        f"2. For each question, a brief tip on how to answer well\n"
        f"3. 3-4 general interview tips specific to this role\n\n"
        f"Return as a JSON object with this structure:\n"
        f'{{"questions": [{{"question": "...", "tip": "..."}}], "general_tips": ["..."]}}\n'
        f"Return ONLY the JSON, nothing else."
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                ),
            ],
            config=types.GenerateContentConfig(
                temperature=0.4,
            ),
        )
        raw = response.text.strip()
        # Try to parse as JSON
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        prep_data = json.loads(raw)
    except Exception as e:
        logger.error("Interview prep error: %s", e)
        return {
            "success": False,
            "message": "Failed to generate interview preparation materials. Please try again.",
            "data": {},
            "action": "prepare_for_interview",
        }

    return {
        "success": True,
        "message": f"Here's your interview preparation for '{vacancy_title}':",
        "data": prep_data,
        "action": "prepare_for_interview",
    }


# ---------------------------------------------------------------------------
# NAVIGATION & GENERAL HANDLERS
# ---------------------------------------------------------------------------

CANDIDATE_PAGE_ROUTES = {
    "dashboard": "/candidate/dashboard",
    "jobs": "/jobs",
    "my-applications": "/candidate/applications",
    "cv-builder": "/candidate/cv-builder",
    "profile": "/candidate/profile",
}


def _handle_candidate_navigate_to_page(*, user, params):
    page = params.get("page", "dashboard")
    path = CANDIDATE_PAGE_ROUTES.get(page, "/candidate/dashboard")

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
