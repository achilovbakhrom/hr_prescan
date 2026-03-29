"""Tool registry: maps tool names to handlers, builds LangChain tools dynamically."""

import json
import logging

from langchain_core.tools import StructuredTool
from pydantic import Field as PydanticField
from pydantic import create_model

from apps.common.ai_assistant.handlers_application import (
    handle_add_candidate_note,
    handle_bulk_update_status,
    handle_list_candidates,
    handle_update_candidate_status,
)
from apps.common.ai_assistant.handlers_company import (
    handle_clear_chat_history,
    handle_invite_hr,
    handle_list_team,
    handle_navigate_to_page,
    handle_toggle_user_active,
)
from apps.common.ai_assistant.handlers_dashboard import (
    handle_get_dashboard,
    handle_get_subscription_info,
    handle_get_usage,
    handle_get_vacancy_summary,
)
from apps.common.ai_assistant.handlers_employer import (
    handle_create_employer,
    handle_create_employer_from_url,
    handle_delete_employer,
    handle_list_employers,
    handle_update_employer,
)
from apps.common.ai_assistant.handlers_interview import (
    handle_cancel_interview,
    handle_list_interviews,
    handle_reset_interview,
)
from apps.common.ai_assistant.handlers_vacancy import (
    handle_archive_vacancy,
    handle_create_vacancy,
    handle_delete_vacancy,
    handle_generate_questions,
    handle_list_vacancies,
    handle_pause_vacancy,
    handle_publish_vacancy,
    handle_regenerate_keywords,
    handle_update_vacancy,
)
from apps.common.ai_assistant.tool_defs_actions import (
    FRONTEND_ACTION_TOOL_DEFINITIONS,
    TEAM_TOOL_DEFINITIONS,
)
from apps.common.ai_assistant.tool_defs_candidate import CANDIDATE_TOOL_DEFINITIONS
from apps.common.ai_assistant.tool_defs_employer import EMPLOYER_TOOL_DEFINITIONS
from apps.common.ai_assistant.tool_defs_interview import (
    DASHBOARD_TOOL_DEFINITIONS,
    INTERVIEW_TOOL_DEFINITIONS,
    SUBSCRIPTION_TOOL_DEFINITIONS,
)
from apps.common.ai_assistant.tool_defs_vacancy import VACANCY_TOOL_DEFINITIONS
from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Aggregated tool definitions from all domain modules
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = (
    VACANCY_TOOL_DEFINITIONS
    + EMPLOYER_TOOL_DEFINITIONS
    + CANDIDATE_TOOL_DEFINITIONS
    + INTERVIEW_TOOL_DEFINITIONS
    + DASHBOARD_TOOL_DEFINITIONS
    + SUBSCRIPTION_TOOL_DEFINITIONS
    + TEAM_TOOL_DEFINITIONS
    + FRONTEND_ACTION_TOOL_DEFINITIONS
)

# ---------------------------------------------------------------------------
# Tool name -> handler function mapping
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "list_vacancies": handle_list_vacancies,
    "create_vacancy": handle_create_vacancy,
    "update_vacancy": handle_update_vacancy,
    "publish_vacancy": handle_publish_vacancy,
    "pause_vacancy": handle_pause_vacancy,
    "archive_vacancy": handle_archive_vacancy,
    "delete_vacancy": handle_delete_vacancy,
    "generate_questions": handle_generate_questions,
    "regenerate_keywords": handle_regenerate_keywords,
    "list_employers": handle_list_employers,
    "create_employer": handle_create_employer,
    "create_employer_from_url": handle_create_employer_from_url,
    "update_employer": handle_update_employer,
    "delete_employer": handle_delete_employer,
    "list_candidates": handle_list_candidates,
    "update_candidate_status": handle_update_candidate_status,
    "bulk_update_status": handle_bulk_update_status,
    "add_candidate_note": handle_add_candidate_note,
    "list_interviews": handle_list_interviews,
    "cancel_interview": handle_cancel_interview,
    "reset_interview": handle_reset_interview,
    "get_dashboard": handle_get_dashboard,
    "get_vacancy_summary": handle_get_vacancy_summary,
    "get_subscription_info": handle_get_subscription_info,
    "get_usage": handle_get_usage,
    "invite_hr": handle_invite_hr,
    "list_team": handle_list_team,
    "toggle_user_active": handle_toggle_user_active,
    "navigate_to_page": handle_navigate_to_page,
    "clear_chat_history": handle_clear_chat_history,
}

JSON_TYPE_MAP = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def execute_tool(*, user, name, args):
    """Execute a tool call and return result dict."""
    handler = TOOL_MAP.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}

    try:
        return handler(user=user, params=args)
    except ApplicationError as e:
        return {"error": str(e.message)}
    except Exception as e:
        logger.error("AI tool %s error: %s", name, e)
        return {"error": str(e)}


def build_langchain_tools(user):
    """Build LangChain StructuredTool list from TOOL_DEFINITIONS, bound to user."""
    tools = []

    for tool_def in TOOL_DEFINITIONS:
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
                    python_type | None,
                    PydanticField(default=None, description=field_desc),
                )

        input_model = create_model(f"{name}_Input", **model_fields)

        # Closure: bind tool_name and user so each tool calls the right handler
        def _make_fn(tool_name, bound_user):
            def fn(**kwargs):
                clean_args = {k: v for k, v in kwargs.items() if v is not None}
                result = execute_tool(user=bound_user, name=tool_name, args=clean_args)
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
