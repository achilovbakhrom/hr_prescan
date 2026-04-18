"""Per-(bot, telegram_id) conversation state, backed by Redis.

Bot flows are inherently multi-turn (e.g. candidate uploads CV, then later
clicks Apply on a vacancy). We persist a small JSON blob in Redis keyed by
``tg_session:<role>:<telegram_id>`` so handlers can resume in-progress flows.

Two bots share the same Redis instance but use disjoint key prefixes via the
``role`` parameter (``hr`` / ``candidate``).
"""

from __future__ import annotations

from typing import Any

from django.core.cache import cache

# Default TTL: long enough that a candidate can upload a CV, take a break,
# then come back and apply, without losing state.
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24h


def _key(*, role: str, telegram_id: int) -> str:
    return f"tg_session:{role}:{telegram_id}"


def get_session(*, role: str, telegram_id: int) -> dict[str, Any]:
    """Return the session dict for a user (empty dict if no session)."""
    return cache.get(_key(role=role, telegram_id=telegram_id), {}) or {}


def save_session(*, role: str, telegram_id: int, data: dict[str, Any]) -> None:
    cache.set(
        _key(role=role, telegram_id=telegram_id),
        data,
        timeout=SESSION_TTL_SECONDS,
    )


def update_session(*, role: str, telegram_id: int, **fields: Any) -> dict[str, Any]:
    """Merge fields into the session and persist. Returns the new session."""
    session = get_session(role=role, telegram_id=telegram_id)
    session.update(fields)
    save_session(role=role, telegram_id=telegram_id, data=session)
    return session


def clear_session(*, role: str, telegram_id: int) -> None:
    cache.delete(_key(role=role, telegram_id=telegram_id))


def clear_session_field(*, role: str, telegram_id: int, field: str) -> None:
    session = get_session(role=role, telegram_id=telegram_id)
    if field in session:
        session.pop(field)
        save_session(role=role, telegram_id=telegram_id, data=session)
