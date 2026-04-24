"""Candidate bot deep-link helpers."""

from __future__ import annotations

from uuid import UUID

from apps.interviews.selectors import get_interview_by_token
from apps.vacancies.models import Vacancy

VACANCY_DEEP_LINK_PREFIX = "vac_"
PRESCREEN_DEEP_LINK_PREFIX = "ps_"


def parse_deep_link_vacancy(*, payload: str) -> UUID | None:
    """Accept both legacy ``vac_<uuid>`` and current ``vac_<telegram_code>`` payloads."""
    if not payload or not payload.startswith(VACANCY_DEEP_LINK_PREFIX):
        return None

    raw = payload[len(VACANCY_DEEP_LINK_PREFIX) :].strip()
    try:
        return UUID(raw)
    except (ValueError, TypeError):
        pass

    if raw.isdigit():
        vacancy = (
            Vacancy.objects.filter(
                telegram_code=int(raw),
                is_deleted=False,
            )
            .only("id")
            .first()
        )
        return vacancy.id if vacancy else None

    return None


def parse_prescreen_token(*, payload: str) -> UUID | None:
    if not payload or not payload.startswith(PRESCREEN_DEEP_LINK_PREFIX):
        return None
    raw = payload[len(PRESCREEN_DEEP_LINK_PREFIX) :].strip()
    try:
        return UUID(raw)
    except (ValueError, TypeError):
        return None


def get_prescreen_interview(*, payload: str):
    token = parse_prescreen_token(payload=payload)
    if token is None:
        return None
    return get_interview_by_token(interview_token=token)
