"""Tool definitions for vacancy-related operations."""

VACANCY_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_vacancies",
            "description": "List company vacancies, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["draft", "published", "paused", "archived"],
                        "description": "Filter by vacancy status",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_vacancy",
            "description": "Create a new job vacancy",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Job title"},
                    "description": {
                        "type": "string",
                        "description": (
                            "Job description. Must be actual job content, "
                            "never meta-commentary like 'no description provided'."
                        ),
                    },
                    "employer_name": {
                        "type": "string",
                        "description": (
                            "Employer company name. Leave empty if not specified "
                            "by user — do NOT fill with explanatory text."
                        ),
                    },
                    "salary_min": {"type": "number"},
                    "salary_max": {"type": "number"},
                    "salary_currency": {"type": "string", "default": "USD"},
                    "location": {"type": "string"},
                    "is_remote": {"type": "boolean"},
                    "employment_type": {
                        "type": "string",
                        "enum": ["full_time", "part_time", "contract", "internship"],
                    },
                    "experience_level": {
                        "type": "string",
                        "enum": ["junior", "middle", "senior", "lead", "director"],
                    },
                    "skills": {
                        "type": "string",
                        "description": "Comma-separated list of skills, e.g. 'Python, Django, React'",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_vacancy",
            "description": (
                "Update an existing vacancy's fields. IMPORTANT: You MUST include the 'updates' parameter "
                "with the new values. Example: vacancy_title='React Developer', "
                "updates={'title': 'Senior React Developer'}"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_title": {"type": "string", "description": "Current title of vacancy to find"},
                    "updates": {
                        "type": "object",
                        "description": (
                            "Object with fields to change. Available fields: title, description, requirements, "
                            "responsibilities, skills, salary_min, salary_max, salary_currency, location, is_remote, "
                            "employment_type, experience_level, deadline, visibility, interview_enabled, cv_required"
                        ),
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "salary_min": {"type": "number"},
                            "salary_max": {"type": "number"},
                            "location": {"type": "string"},
                            "is_remote": {"type": "boolean"},
                        },
                    },
                },
                "required": ["vacancy_title", "updates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "publish_vacancy",
            "description": "Publish a draft or paused vacancy",
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pause_vacancy",
            "description": "Pause a published vacancy",
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "archive_vacancy",
            "description": "Archive a published or paused vacancy",
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_vacancy",
            "description": (
                "Permanently delete a draft or archived vacancy. "
                "Cannot delete published or paused vacancies."
            ),
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_questions",
            "description": (
                "AI-generate competencies (skill goals) for prescanning or interview. These are NOT literal questions "
                "— they are skills/knowledge areas the AI interviewer will evaluate candidates on through conversation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_title": {"type": "string"},
                    "step": {"type": "string", "enum": ["prescanning", "interview"], "default": "prescanning"},
                },
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "regenerate_keywords",
            "description": "AI-regenerate search keywords for a vacancy",
            "parameters": {
                "type": "object",
                "properties": {"vacancy_title": {"type": "string"}},
                "required": ["vacancy_title"],
            },
        },
    },
]
