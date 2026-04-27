from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.job_parser.services.normalization import (
    dedupe_skills,
    make_fingerprint,
    normalize_currency,
    normalize_decimal,
    normalize_employment,
)
from apps.vacancies.models import Vacancy
from apps.vacancies.services import create_vacancy


@transaction.atomic
def upsert_parsed_vacancy(*, source: ParsedVacancySource, payload: dict) -> ParsedVacancy:
    now = timezone.now()
    title = str(payload.get("title") or "").strip()
    external_id = str(payload.get("external_id") or "").strip()
    if not title or not external_id:
        raise ApplicationError("Parsed vacancy requires title and external_id.")

    defaults = _build_defaults(payload=payload, now=now)
    defaults["fingerprint"] = make_fingerprint(
        title=title,
        company_name=defaults["company_name"],
        location=defaults["location"],
    )
    vacancy, created = ParsedVacancy.objects.update_or_create(
        source=source,
        external_id=external_id,
        defaults={"title": title, **defaults},
    )
    if not created and vacancy.imported_vacancy_id and vacancy.status != ParsedVacancy.Status.IMPORTED:
        vacancy.status = ParsedVacancy.Status.IMPORTED
        vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def refresh_source_actuality(*, source: ParsedVacancySource, sync_started_at: timezone.datetime) -> int:
    qs = source.vacancies.exclude(status__in=[ParsedVacancy.Status.IMPORTED, ParsedVacancy.Status.CLOSED])
    stale_count = qs.filter(last_seen_at__lt=sync_started_at).update(
        status=ParsedVacancy.Status.STALE,
        actuality_reason="Not present in the latest source sync.",
        updated_at=timezone.now(),
    )
    expired_count = qs.filter(expires_at__lt=timezone.now()).update(
        status=ParsedVacancy.Status.EXPIRED,
        actuality_reason="External vacancy expiration date has passed.",
        updated_at=timezone.now(),
    )
    return stale_count + expired_count


def refresh_telegram_actuality() -> int:
    updated = 0
    sources = ParsedVacancySource.objects.filter(
        source_type=ParsedVacancySource.Type.TELEGRAM,
        is_active=True,
    )
    for source in sources:
        ttl_days = int((source.settings or {}).get("ttl_days", 30))
        threshold = timezone.now() - timedelta(days=ttl_days)
        updated += source.vacancies.filter(
            status=ParsedVacancy.Status.ACTIVE,
            last_seen_at__lt=threshold,
        ).update(
            status=ParsedVacancy.Status.STALE,
            actuality_reason=f"Telegram vacancy was not refreshed for {ttl_days} days.",
            updated_at=timezone.now(),
        )
    return updated


@transaction.atomic
def import_parsed_vacancy(*, parsed_vacancy: ParsedVacancy, created_by) -> Vacancy:
    if parsed_vacancy.imported_vacancy_id:
        raise ApplicationError("Parsed vacancy has already been imported.")
    if parsed_vacancy.status in (ParsedVacancy.Status.CLOSED, ParsedVacancy.Status.EXPIRED):
        raise ApplicationError("Closed or expired parsed vacancies cannot be imported.")

    vacancy = create_vacancy(
        company=parsed_vacancy.source.company,
        created_by=created_by,
        title=parsed_vacancy.title,
        description=parsed_vacancy.description or parsed_vacancy.responsibilities or parsed_vacancy.title,
        requirements=parsed_vacancy.requirements,
        responsibilities=parsed_vacancy.responsibilities,
        skills=parsed_vacancy.skills,
        salary_min=parsed_vacancy.salary_min,
        salary_max=parsed_vacancy.salary_max,
        salary_currency=parsed_vacancy.salary_currency,
        location=parsed_vacancy.location,
        employment_type=normalize_employment(parsed_vacancy.employment_type),
        visibility=Vacancy.Visibility.PRIVATE,
        status=Vacancy.Status.DRAFT,
    )
    parsed_vacancy.imported_vacancy = vacancy
    parsed_vacancy.status = ParsedVacancy.Status.IMPORTED
    parsed_vacancy.actuality_reason = "Imported into internal vacancy draft."
    parsed_vacancy.save(update_fields=["imported_vacancy", "status", "actuality_reason", "updated_at"])
    return vacancy


def _build_defaults(*, payload: dict, now: timezone.datetime) -> dict:
    status = payload.get("status") or ParsedVacancy.Status.ACTIVE
    return {
        "external_url": str(payload.get("external_url") or ""),
        "company_name": str(payload.get("company_name") or ""),
        "description": str(payload.get("description") or ""),
        "requirements": str(payload.get("requirements") or ""),
        "responsibilities": str(payload.get("responsibilities") or ""),
        "skills": dedupe_skills(list(payload.get("skills") or [])),
        "salary_min": normalize_decimal(payload.get("salary_min")),
        "salary_max": normalize_decimal(payload.get("salary_max")),
        "salary_currency": normalize_currency(payload.get("salary_currency")),
        "location": str(payload.get("location") or ""),
        "employment_type": str(payload.get("employment_type") or ""),
        "published_at": payload.get("published_at"),
        "expires_at": payload.get("expires_at"),
        "last_seen_at": now,
        "status": status,
        "actuality_reason": str(payload.get("actuality_reason") or ""),
        "raw_payload": dict(payload.get("raw_payload") or {}),
    }
