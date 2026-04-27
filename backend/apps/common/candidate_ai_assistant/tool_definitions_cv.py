from apps.common.candidate_ai_assistant.tool_schemas_cv import (
    CERTIFICATION_ITEM_SCHEMA,
    EDUCATION_ITEM_SCHEMA,
    LANGUAGE_ITEM_SCHEMA,
    WORK_EXPERIENCE_ITEM_SCHEMA,
)

CV_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "improve_cv_section",
            "description": (
                "AI-powered CV text improvement. Rewrites a section of the candidate's CV "
                "to be more professional and impactful."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["headline", "summary", "experience_description"],
                        "description": "Which CV section to improve",
                    },
                    "content": {
                        "type": "string",
                        "description": "The current text of the CV section to improve",
                    },
                    "job_title": {
                        "type": "string",
                        "description": "Target job title to tailor the improvement for",
                    },
                },
                "required": ["section", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_skills",
            "description": (
                "AI-powered skill suggestions based on a job title or description. "
                "Helps candidates identify relevant skills to highlight."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {
                        "type": "string",
                        "description": "Job title to suggest skills for",
                    },
                    "description": {
                        "type": "string",
                        "description": "Job description or role context",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_cv_status",
            "description": (
                "Read the candidate's current CV state and completeness. Call this BEFORE "
                "starting a CV-build conversation so you know what's already filled in and "
                "only ask for what's missing."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_my_cv",
            "description": (
                "Save the candidate's CV data after collecting it through conversation. "
                "Call this ONCE at the end of a CV-build dialogue, with all collected fields. "
                "Pass arrays of objects for work_experiences, educations, languages, certifications. "
                "Skills is a flat string array. Only include fields the candidate confirmed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "headline": {
                        "type": "string",
                        "description": "Desired job title / position headline",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Professional summary paragraph",
                    },
                    "location": {
                        "type": "string",
                        "description": "City, country",
                    },
                    "desired_employment_type": {
                        "type": "string",
                        "enum": ["full_time", "part_time", "contract", "internship"],
                        "description": "Preferred employment type",
                    },
                    "desired_salary_min": {
                        "type": "number",
                        "description": "Minimum desired salary as a number (omit if negotiable)",
                    },
                    "desired_salary_max": {
                        "type": "number",
                        "description": "Maximum desired salary as a number (omit if negotiable)",
                    },
                    "desired_salary_currency": {
                        "type": "string",
                        "description": "ISO currency code, e.g. USD, EUR, UZS",
                    },
                    "desired_salary_negotiable": {
                        "type": "boolean",
                        "description": "True if the candidate said salary is negotiable",
                    },
                    "work_experiences": {
                        "type": "array",
                        "description": (
                            "Array of {company_name, position, employment_type, location, "
                            "start_date (YYYY-MM-DD), end_date (YYYY-MM-DD or null), is_current, description}"
                        ),
                        "items": WORK_EXPERIENCE_ITEM_SCHEMA,
                    },
                    "educations": {
                        "type": "array",
                        "description": (
                            "Array of {institution, degree, field_of_study, "
                            "start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), description}"
                        ),
                        "items": EDUCATION_ITEM_SCHEMA,
                    },
                    "skills": {
                        "type": "array",
                        "description": "Flat array of skill names as strings",
                        "items": {"type": "string"},
                    },
                    "languages": {
                        "type": "array",
                        "description": (
                            "Array of {language: name, proficiency: beginner|intermediate|advanced|native}"
                        ),
                        "items": LANGUAGE_ITEM_SCHEMA,
                    },
                    "certifications": {
                        "type": "array",
                        "description": "Array of {name, issuing_organization, issue_date (YYYY-MM-DD)}",
                        "items": CERTIFICATION_ITEM_SCHEMA,
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_cv_pdf",
            "description": (
                "Generate a downloadable PDF CV from the candidate's saved profile data. "
                "Only call this AFTER build_my_cv (or when the candidate explicitly asks for the PDF). "
                "The candidate's profile must already contain at least basic info."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "template_name": {
                        "type": "string",
                        "enum": ["classic", "modern", "minimal"],
                        "description": "PDF template to use (default: classic)",
                    },
                    "cv_name": {
                        "type": "string",
                        "description": "Friendly name for the generated CV record",
                    },
                },
            },
        },
    },
]
