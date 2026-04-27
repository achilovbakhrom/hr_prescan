from __future__ import annotations

import hashlib
import re

from django.utils import timezone

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services.normalization import clean_text
from apps.job_parser.services.parsed_vacancy_crud import upsert_parsed_vacancy

SALARY_RE = re.compile(
    r"(?P<from>\d[\d\s.,]*)\s*(?:-|\u0434\u043e|to)?\s*"
    r"(?P<to>\d[\d\s.,]*)?\s*(?P<cur>usd|eur|rub|uzs|\u0441\u0443\u043c)?",
    re.I,
)
LABEL_RE = re.compile(
    r"^(salary|\u0437\u0430\u0440\u043f\u043b\u0430\u0442\u0430|\u043c\u0430\u043e\u0448|"
    r"location|\u043b\u043e\u043a\u0430\u0446\u0438\u044f|requirements|\u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d\u0438\u044f)\b",
    re.I,
)
HASHTAG_RE = re.compile(r"#([^\s#]+)")


def parse_telegram_job_message(
    *,
    source: ParsedVacancySource,
    message_text: str,
    message_id: str = "",
    message_url: str = "",
    published_at=None,
) -> ParsedVacancy:
    if source.source_type != ParsedVacancySource.Type.TELEGRAM:
        raise ApplicationError("Source is not a Telegram source.")

    text = clean_text(message_text)
    if not text:
        raise ApplicationError("Telegram message text is empty.")

    title = _guess_title(message_text)
    salary_min, salary_max, currency = _guess_salary(text)
    payload = {
        "external_id": message_id or hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "external_url": message_url,
        "title": title,
        "description": message_text.strip(),
        "requirements": "",
        "responsibilities": "",
        "skills": _guess_skills(message_text),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": currency,
        "location": _guess_location(message_text),
        "employment_type": "",
        "published_at": published_at or timezone.now(),
        "status": ParsedVacancy.Status.ACTIVE,
        "actuality_reason": "Telegram posts are treated as active until TTL/manual refresh marks them stale.",
        "raw_payload": {"message_text": message_text, "message_id": message_id, "message_url": message_url},
    }
    return upsert_parsed_vacancy(source=source, payload=payload)


def _guess_title(message_text: str) -> str:
    for raw_line in message_text.splitlines():
        line = clean_text(raw_line).strip("- ")
        if line and not LABEL_RE.match(line):
            return line[:255]
    return "Telegram vacancy"


def _guess_salary(text: str) -> tuple[str | None, str | None, str]:
    match = SALARY_RE.search(text)
    if not match:
        return None, None, "USD"
    salary_from = _clean_number(match.group("from"))
    salary_to = _clean_number(match.group("to"))
    currency = (match.group("cur") or "USD").upper()
    if currency in {"\u0421\u0423\u041c", "UZS"}:
        currency = "UZS"
    return salary_from, salary_to, currency[:3]


def _guess_location(message_text: str) -> str:
    labels = ("location", "\u043b\u043e\u043a\u0430\u0446\u0438\u044f", "\u0433\u043e\u0440\u043e\u0434")
    for raw_line in message_text.splitlines():
        line = clean_text(raw_line)
        if line.casefold().startswith(labels):
            return line.split(":", 1)[-1].strip()[:255]
    return ""


def _guess_skills(message_text: str) -> list[str]:
    tags = [tag.replace("_", " ") for tag in HASHTAG_RE.findall(message_text)]
    return [tag for tag in tags if len(tag) > 1]


def _clean_number(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"[^\d.]", "", value.replace(",", "."))
