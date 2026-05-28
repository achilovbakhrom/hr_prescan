"""Tool definitions for AI-generated vacancy setup."""

VACANCY_GENERATION_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "generate_questions",
            "description": (
                "AI-generate optional sample question seeds for prescanning or interview. "
                "Prefer generate_instructions for the primary screening setup."
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
            "name": "generate_instructions",
            "description": (
                "AI-generate editable screening instructions for prescanning or interview. "
                "Instructions can contain topics, tone, strictness, red flags, and sample questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_title": {"type": "string"},
                    "step": {"type": "string", "enum": ["prescanning", "interview"], "default": "prescanning"},
                    "style": {"type": "string", "enum": ["light", "balanced", "strict"], "default": "balanced"},
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
