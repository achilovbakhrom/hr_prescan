"""Agent entry point: process_ai_command and response builders."""

import json
import logging

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from apps.common.ai_assistant.prompts import SYSTEM_PROMPT
from apps.common.ai_assistant.tools import build_langchain_tools

logger = logging.getLogger(__name__)


def process_ai_command(*, user, message, context=None):
    """Process a natural language command using a LangChain agent.

    The agent can call multiple tools in sequence to fulfill complex requests
    like: "Create a Python Developer vacancy at TechCorp, publish it,
    and generate competencies"
    """
    from django.conf import settings

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0.1,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    tools = build_langchain_tools(user)

    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)

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

        from langchain_core.messages import ToolMessage

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
        logger.error("AI assistant error: %s", e, exc_info=True)
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
            message += "\n\n\u26a0\ufe0f Some actions encountered errors:\n" + "\n".join(error_details)

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
            message += f"\n\n\u2705 {len(successful)} action(s) completed before the error."
    return {
        "success": False,
        "message": message,
        "actions": actions_taken,
    }
