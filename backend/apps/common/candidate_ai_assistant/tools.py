import json
import logging

from langchain_core.tools import StructuredTool
from pydantic import Field as PydanticField
from pydantic import create_model

from apps.common.candidate_ai_assistant.handlers_application import (
    _handle_get_application_details,
    _handle_list_my_applications,
)
from apps.common.candidate_ai_assistant.handlers_cv import (
    _handle_build_my_cv,
    _handle_generate_cv_pdf,
    _handle_get_my_cv_status,
)
from apps.common.candidate_ai_assistant.handlers_interview import (
    _handle_prepare_for_interview,
)
from apps.common.candidate_ai_assistant.handlers_job import (
    _handle_get_job_details,
    _handle_search_jobs,
)
from apps.common.candidate_ai_assistant.handlers_navigation import (
    _handle_candidate_clear_chat_history,
    _handle_candidate_navigate_to_page,
)
from apps.common.candidate_ai_assistant.handlers_profile import (
    _handle_improve_cv_section,
    _handle_suggest_skills,
)
from apps.common.candidate_ai_assistant.tool_definitions import CANDIDATE_TOOL_DEFINITIONS
from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool executor — maps tool names to handler functions
# ---------------------------------------------------------------------------

CANDIDATE_TOOL_MAP = {
    "search_jobs": _handle_search_jobs,
    "get_job_details": _handle_get_job_details,
    "list_my_applications": _handle_list_my_applications,
    "get_application_details": _handle_get_application_details,
    "improve_cv_section": _handle_improve_cv_section,
    "suggest_skills": _handle_suggest_skills,
    "get_my_cv_status": _handle_get_my_cv_status,
    "build_my_cv": _handle_build_my_cv,
    "generate_cv_pdf": _handle_generate_cv_pdf,
    "prepare_for_interview": _handle_prepare_for_interview,
    "navigate_to_page": _handle_candidate_navigate_to_page,
    "clear_chat_history": _handle_candidate_clear_chat_history,
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
    handler = CANDIDATE_TOOL_MAP.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}

    try:
        return handler(user=user, params=args)
    except ApplicationError as e:
        return {"error": str(e.message)}
    except Exception as e:
        logger.error("Candidate AI tool %s error: %s", name, e)
        return {"error": str(e)}


def build_langchain_tools(user):
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
                    python_type | None,
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
