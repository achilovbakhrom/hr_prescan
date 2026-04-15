"""Tool definitions for candidate-related operations."""

CANDIDATE_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_candidates",
            "description": "List candidates for a vacancy",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_title": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "applied",
                            "prescanned",
                            "interviewed",
                            "shortlisted",
                            "hired",
                            "rejected",
                            "expired",
                            "archived",
                        ],
                    },
                },
                "required": ["vacancy_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_candidate_status",
            "description": "Change a candidate's pipeline status",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_email_or_name": {"type": "string"},
                    "vacancy_title": {"type": "string"},
                    "new_status": {
                        "type": "string",
                        "enum": [
                            "applied",
                            "prescanned",
                            "interviewed",
                            "shortlisted",
                            "hired",
                            "rejected",
                            "archived",
                        ],
                    },
                },
                "required": ["candidate_email_or_name", "new_status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bulk_update_status",
            "description": "Move all candidates from one status to another for a vacancy",
            "parameters": {
                "type": "object",
                "properties": {
                    "vacancy_title": {"type": "string"},
                    "from_status": {"type": "string"},
                    "to_status": {"type": "string"},
                },
                "required": ["vacancy_title", "from_status", "to_status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_candidate_note",
            "description": "Add an HR note to a candidate's application",
            "parameters": {
                "type": "object",
                "properties": {
                    "candidate_email_or_name": {"type": "string"},
                    "vacancy_title": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["candidate_email_or_name", "note"],
            },
        },
    },
]
