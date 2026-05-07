from __future__ import annotations

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services.hh_api import HH_API_BASE_URLS, hh_get
from apps.job_parser.services.normalization import clean_text, has_contact_info
from apps.job_parser.services.parsed_vacancy_crud import refresh_source_actuality, upsert_parsed_vacancy


def sync_hh_source(*, source: ParsedVacancySource) -> dict:
    if source.source_type not in HH_API_BASE_URLS:
        raise ApplicationError("Source is not a HeadHunter source.")

    sync_started_at = timezone.now()
    checkpoint_external_id = source.last_seen_external_id
    items, reached_checkpoint = _fetch_hh_items(source=source, checkpoint_external_id=checkpoint_external_id)
    parsed_count = 0
    skipped_no_contact = 0

    for item in items:
        if _stop_requested(source=source):
            return {"parsed": parsed_count, "skipped_no_contact": skipped_no_contact, "cancelled": True}
        detail = (
            _fetch_hh_detail(source=source, vacancy_id=item["id"])
            if source.settings.get("fetch_details", True) or source.settings.get("require_contact", True)
            else {}
        )
        payload = _map_hh_item(item=item, detail=detail)
        if not _has_hh_contact(item=item, detail=detail) and not payload["external_url"]:
            skipped_no_contact += 1
            continue
        upsert_parsed_vacancy(source=source, payload=payload)
        parsed_count += 1

    stale_count = refresh_source_actuality(
        source=source,
        sync_started_at=sync_started_at,
        mark_missing_stale=not bool(checkpoint_external_id),
    )
    update_fields = ["last_synced_at", "updated_at"]
    source.last_synced_at = timezone.now()
    if items:
        source.last_seen_external_id = str(items[0].get("id") or "")
        source.last_seen_published_at = _parse_hh_datetime(items[0].get("published_at"))
        update_fields.extend(["last_seen_external_id", "last_seen_published_at"])
    source.save(update_fields=update_fields)
    return {
        "parsed": parsed_count,
        "skipped_no_contact": skipped_no_contact,
        "stale_or_expired": stale_count,
        "reached_checkpoint": reached_checkpoint,
    }


def _fetch_hh_items(*, source: ParsedVacancySource, checkpoint_external_id: str = "") -> tuple[list[dict], bool]:
    settings = source.settings or {}
    first_page = int(settings.get("page", 0))
    max_pages = max(1, min(int(settings.get("max_pages", 20)), 20))
    items: list[dict] = []
    reached_checkpoint = False
    for page in range(first_page, first_page + max_pages):
        if _stop_requested(source=source):
            break
        params = {
            "text": settings.get("text", ""),
            "area": settings.get("area", ""),
            "employer_id": settings.get("employer_id", ""),
            "per_page": min(int(settings.get("per_page", 100)), 100),
            "page": page,
        }
        response = hh_get(
            source=source,
            path="/vacancies",
            params={key: value for key, value in params.items() if value not in ("", None)},
        )
        for item in response.get("items") or []:
            if checkpoint_external_id and str(item.get("id") or "") == checkpoint_external_id:
                reached_checkpoint = True
                break
            items.append(item)
        if reached_checkpoint:
            break
        if page + 1 >= int(response.get("pages") or 0):
            break
    return items, reached_checkpoint


def _stop_requested(*, source: ParsedVacancySource) -> bool:
    return ParsedVacancySource.objects.filter(
        id=source.id,
        sync_status__in=[
            ParsedVacancySource.SyncStatus.STOPPING,
            ParsedVacancySource.SyncStatus.CANCELLED,
        ],
    ).exists()


def _fetch_hh_detail(*, source: ParsedVacancySource, vacancy_id: str) -> dict:
    try:
        return hh_get(source=source, path=f"/vacancies/{vacancy_id}", params={})
    except ApplicationError:
        return {}


def _has_hh_contact(*, item: dict, detail: dict) -> bool:
    contacts = detail.get("contacts") or item.get("contacts") or {}
    if contacts.get("email"):
        return True
    if contacts.get("phones"):
        return True
    return has_contact_info(contacts) or has_contact_info(detail.get("description"))


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
