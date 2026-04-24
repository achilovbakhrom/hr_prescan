WORK_EXPERIENCE_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "position": {"type": "string"},
        "employment_type": {
            "type": "string",
            "enum": ["full_time", "part_time", "contract", "internship"],
        },
        "location": {"type": "string"},
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "is_current": {"type": "boolean"},
        "description": {"type": "string"},
    },
}

EDUCATION_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "institution": {"type": "string"},
        "degree": {"type": "string"},
        "field_of_study": {"type": "string"},
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "description": {"type": "string"},
    },
}

LANGUAGE_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "language": {"type": "string"},
        "proficiency": {
            "type": "string",
            "enum": ["beginner", "intermediate", "advanced", "native"],
        },
    },
}

CERTIFICATION_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "issuing_organization": {"type": "string"},
        "issue_date": {"type": "string"},
    },
}
