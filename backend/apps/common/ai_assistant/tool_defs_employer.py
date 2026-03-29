"""Tool definitions for employer-related operations."""

EMPLOYER_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_employers",
            "description": "List employer companies",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_employer",
            "description": "Create a new employer company",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "industry": {"type": "string"},
                    "website": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_employer_from_url",
            "description": "Create employer by parsing a website URL with AI",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "url": {"type": "string"}},
                "required": ["name", "url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_employer",
            "description": "Update an employer company",
            "parameters": {
                "type": "object",
                "properties": {"employer_name": {"type": "string"}, "updates": {"type": "object"}},
                "required": ["employer_name", "updates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_employer",
            "description": "Delete an employer company (only if no vacancies linked)",
            "parameters": {
                "type": "object",
                "properties": {"employer_name": {"type": "string"}},
                "required": ["employer_name"],
            },
        },
    },
]
