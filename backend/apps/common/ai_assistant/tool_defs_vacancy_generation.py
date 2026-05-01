"""Tool definitions for AI-generated vacancy setup."""

VACANCY_GENERATION_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "generate_questions",
            "description": (
                "AI-generate literal candidate-facing questions for prescanning or interview. "
                "These questions are stored and asked directly to candidates."
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
            "name": "generate_criteria",
            "description": (
                "AI-generate role-specific evaluation criteria/competencies for prescanning or interview. "
                "These criteria are used by the AI to score candidates."
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
