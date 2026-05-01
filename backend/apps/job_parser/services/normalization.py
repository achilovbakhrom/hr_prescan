from __future__ import annotations

import hashlib
import re
from decimal import Decimal, InvalidOperation
from html import unescape

from django.utils.html import strip_tags

from apps.vacancies.models import Vacancy

WHITESPACE_RE = re.compile(r"\s+")
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
TELEGRAM_RE = re.compile(r"(?:https?://)?t\.me/[A-Za-z0-9_]+|@[A-Za-z0-9_]{4,}", re.I)


def clean_text(value: object) -> str:
    text = strip_tags(str(value or ""))
    return WHITESPACE_RE.sub(" ", unescape(text)).strip()


def has_contact_info(value: object) -> bool:
    text = clean_text(value)
    if EMAIL_RE.search(text) or TELEGRAM_RE.search(text):
        return True
    for match in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) >= 9:
            return True
    return False


def make_fingerprint(*, title: str, company_name: str = "", location: str = "") -> str:
    value = "|".join(clean_text(part).casefold() for part in (title, company_name, location))
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_currency(value: object) -> str:
    currency = str(value or "USD").upper()[:3]
    return currency if len(currency) == 3 else "USD"


def normalize_decimal(value: object) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def normalize_employment(value: object) -> str:
    text = clean_text(value).casefold().replace("-", "_")
    mapping = {
        "full": Vacancy.EmploymentType.FULL_TIME,
        "full_time": Vacancy.EmploymentType.FULL_TIME,
        "полная": Vacancy.EmploymentType.FULL_TIME,
        "part": Vacancy.EmploymentType.PART_TIME,
        "part_time": Vacancy.EmploymentType.PART_TIME,
        "частичная": Vacancy.EmploymentType.PART_TIME,
        "contract": Vacancy.EmploymentType.CONTRACT,
        "проектная": Vacancy.EmploymentType.CONTRACT,
        "internship": Vacancy.EmploymentType.INTERNSHIP,
        "стажировка": Vacancy.EmploymentType.INTERNSHIP,
    }
    for token, result in mapping.items():
        if token in text:
            return result
    return Vacancy.EmploymentType.FULL_TIME


def dedupe_skills(values: list[object]) -> list[str]:
    seen: set[str] = set()
    skills: list[str] = []
    for value in values:
        skill = clean_text(value)
        key = skill.casefold()
        if skill and key not in seen:
            skills.append(skill[:100])
            seen.add(key)
    return skills
