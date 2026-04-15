"""Tool definitions for interview, dashboard, and subscription operations."""

INTERVIEW_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_interviews",
            "description": "List interviews, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled", "expired"],
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_interview",
            "description": "Cancel a pending or in-progress interview",
            "parameters": {
                "type": "object",
                "properties": {"candidate_email_or_name": {"type": "string"}},
                "required": ["candidate_email_or_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_interview",
            "description": "Reset an abandoned interview (creates a new session)",
            "parameters": {
                "type": "object",
                "properties": {"candidate_email_or_name": {"type": "string"}},
                "required": ["candidate_email_or_name"],
            },
        },
    },
]

DASHBOARD_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_dashboard",
            "description": "Get dashboard statistics (active vacancies, candidates, interviews)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_vacancy_summary",
            "description": "Get detailed pipeline summary for a specific vacancy",
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
]

SUBSCRIPTION_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_subscription_info",
            "description": "Get current subscription plan info",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_usage",
            "description": "Get current usage stats (vacancies, interviews, storage)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
