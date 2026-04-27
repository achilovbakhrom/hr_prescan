from __future__ import annotations

import requests
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services.normalization import clean_text
from apps.job_parser.services.parsed_vacancy_crud import refresh_source_actuality, upsert_parsed_vacancy

HH_API_BASE_URLS = {
    ParsedVacancySource.Type.HH_RU: "https://api.hh.ru",
    ParsedVacancySource.Type.HH_UZ: "https://api.hh.uz",
}


def sync_hh_source(*, source: ParsedVacancySource) -> dict:
    if source.source_type not in HH_API_BASE_URLS:
        raise ApplicationError("Source is not a HeadHunter source.")

    sync_started_at = timezone.now()
    items = _fetch_hh_items(source=source)
    parsed_count = 0

    for item in items:
        detail = _fetch_hh_detail(source=source, vacancy_id=item["id"]) if source.settings.get("fetch_details") else {}
        upsert_parsed_vacancy(source=source, payload=_map_hh_item(item=item, detail=detail))
        parsed_count += 1

    stale_count = refresh_source_actuality(source=source, sync_started_at=sync_started_at)
    source.last_synced_at = timezone.now()
    source.save(update_fields=["last_synced_at", "updated_at"])
    return {"parsed": parsed_count, "stale_or_expired": stale_count}


def _fetch_hh_items(*, source: ParsedVacancySource) -> list[dict]:
    settings = source.settings or {}
    first_page = int(settings.get("page", 0))
    max_pages = max(1, min(int(settings.get("max_pages", 1)), 20))
    items: list[dict] = []
    for page in range(first_page, first_page + max_pages):
        params = {
            "text": settings.get("text", ""),
            "area": settings.get("area", ""),
            "employer_id": settings.get("employer_id", ""),
            "per_page": min(int(settings.get("per_page", 20)), 100),
            "page": page,
        }
        response = _hh_get(
            source=source,
            path="/vacancies",
            params={key: value for key, value in params.items() if value not in ("", None)},
        )
        items.extend(response.get("items") or [])
        if page + 1 >= int(response.get("pages") or 0):
            break
    return items


def _fetch_hh_detail(*, source: ParsedVacancySource, vacancy_id: str) -> dict:
    try:
        return _hh_get(source=source, path=f"/vacancies/{vacancy_id}", params={})
    except ApplicationError:
        return {}


def _hh_get(*, source: ParsedVacancySource, path: str, params: dict) -> dict:
    base_url = HH_API_BASE_URLS[source.source_type]
    try:
        response = requests.get(
            f"{base_url}{path}",
            params=params,
            headers={"User-Agent": "HR PreScan vacancy parser"},
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ApplicationError("HeadHunter source sync failed.") from exc
    return response.json()


def _map_hh_item(*, item: dict, detail: dict) -> dict:
    salary = item.get("salary") or detail.get("salary") or {}
    employer = item.get("employer") or detail.get("employer") or {}
    area = item.get("area") or detail.get("area") or {}
    snippet = item.get("snippet") or {}
    employment = item.get("employment") or detail.get("employment") or {}
    description = clean_text(detail.get("description") or snippet.get("responsibility") or "")
    requirements = clean_text(snippet.get("requirement") or "")
    key_skills = [skill.get("name") for skill in detail.get("key_skills") or [] if skill.get("name")]
    archived = bool(item.get("archived") or detail.get("archived"))
    status = ParsedVacancy.Status.CLOSED if archived else ParsedVacancy.Status.ACTIVE
    return {
        "external_id": str(item.get("id") or detail.get("id")),
        "external_url": item.get("alternate_url") or detail.get("alternate_url") or "",
        "title": item.get("name") or detail.get("name") or "",
        "company_name": employer.get("name", ""),
        "description": description,
        "requirements": requirements,
        "responsibilities": description,
        "skills": key_skills,
        "salary_min": salary.get("from"),
        "salary_max": salary.get("to"),
        "salary_currency": salary.get("currency"),
        "location": area.get("name", ""),
        "employment_type": employment.get("name", ""),
        "published_at": _parse_hh_datetime(item.get("published_at") or detail.get("published_at")),
        "expires_at": _parse_hh_datetime(detail.get("expires_at")),
        "status": status,
        "actuality_reason": "Archived on HeadHunter." if archived else "",
        "raw_payload": detail or item,
    }


def _parse_hh_datetime(value: object):
    if not value:
        return None
    parsed = parse_datetime(str(value))
    if parsed and timezone.is_naive(parsed):
        return timezone.make_aware(parsed)
    return parsed
