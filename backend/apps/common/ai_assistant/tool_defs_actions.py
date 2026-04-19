"""Tool definitions for team management and frontend actions."""

TEAM_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "invite_hr",
            "description": "Invite a new HR manager to the team",
            "parameters": {
                "type": "object",
                "properties": {"email": {"type": "string"}},
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_team",
            "description": "List team members",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_user_active",
            "description": "Activate or deactivate a team member",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "activate": {"type": "boolean"},
                },
                "required": ["email", "activate"],
            },
        },
    },
]

FRONTEND_ACTION_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "navigate_to_page",
            "description": (
                "Navigate the user to a specific page in the app. Use after creating/updating resources "
                "or when user asks to go somewhere. Available pages: dashboard, vacancies, vacancy-detail "
                "(needs vacancy_id), companies, company-create, candidates, interviews, settings, profile, "
                "team, pricing, subscription, notifications, jobs (public job board)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": (
                            "Page name: dashboard, vacancies, vacancy-detail, companies, company-create, "
                            "candidates, interviews, settings, profile, team, pricing, subscription, "
                            "notifications, jobs"
                        ),
                    },
                    "params": {
                        "type": "object",
                        "description": 'Route params if needed, e.g. {"id": "vacancy-uuid"} for vacancy-detail',
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
            "description": (
                "Clear the AI assistant chat history. Use when user asks to clear history, "
                "reset conversation, or start fresh."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
