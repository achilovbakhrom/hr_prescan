import json
import re
from typing import Any

VACANCY_CONTENT_ALIASES = {
    "description": ("description", "job_description", "vacancy_description", "role_description"),
    "requirements": ("requirements", "qualifications", "candidate_requirements"),
    "responsibilities": ("responsibilities", "duties", "job_responsibilities", "role_responsibilities"),
}


def load_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, flags=re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)
    elif not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            cleaned = cleaned[start : end + 1]

    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    return data


def normalize_vacancy_content(data: dict[str, Any]) -> dict[str, str]:
    source = _content_source(data)
    return {field: _first_text(source, aliases) for field, aliases in VACANCY_CONTENT_ALIASES.items()}


def has_complete_vacancy_content(content: dict[str, str]) -> bool:
    return all(content.get(field, "").strip() for field in VACANCY_CONTENT_ALIASES)


def require_complete_vacancy_content(content: dict[str, str]) -> dict[str, str]:
    if not has_complete_vacancy_content(content):
        raise ValueError("AI returned empty vacancy content")
    return content


def _content_source(data: dict[str, Any]) -> dict[str, Any]:
    if any(key in data for aliases in VACANCY_CONTENT_ALIASES.values() for key in aliases):
        return data
    for key in ("content", "vacancy", "job"):
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return data


def _first_text(data: dict[str, Any], aliases: tuple[str, ...]) -> str:
    for key in aliases:
        value = data.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return ""
