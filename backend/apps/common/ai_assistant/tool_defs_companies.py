"""Tool definitions for per-user Company CRUD operations."""

COMPANY_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_companies",
            "description": "List the user's companies (excludes soft-deleted).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_company",
            "description": "Create a new company. Becomes default only if user has no other companies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Company name"},
                    "size": {
                        "type": "string",
                        "enum": ["small", "medium", "large", "enterprise"],
                        "description": "Company size bucket",
                    },
                    "country": {"type": "string"},
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
            "name": "update_company",
            "description": "Update a company the user owns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "updates": {"type": "object"},
                },
                "required": ["company_name", "updates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_company",
            "description": (
                "Soft-delete a company. Fails if it's the user's only remaining company. "
                "Transfers the default flag to the next company (by creation date) if needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {"company_name": {"type": "string"}},
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_default_company",
            "description": "Mark a company as the user's default (used implicitly for new vacancies).",
            "parameters": {
                "type": "object",
                "properties": {"company_name": {"type": "string"}},
                "required": ["company_name"],
            },
        },
    },
]
