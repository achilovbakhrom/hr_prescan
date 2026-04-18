from apps.common.candidate_ai_assistant.tool_definitions_cv import CV_TOOL_DEFINITIONS

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
    *CV_TOOL_DEFINITIONS,
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
