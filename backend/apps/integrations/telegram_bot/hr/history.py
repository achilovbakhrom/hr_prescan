"""HR bot conversation history (Redis-backed, last N turns).

Extracted from the original handlers.py so the routing module stays under the
200-line limit. The HR LangChain agent uses this for multi-turn context.
"""
from __future__ import annotations

from django.core.cache import cache

HISTORY_KEY_TEMPLATE = "tg_history:{telegram_id}"
HISTORY_TTL_SECONDS = 60 * 60 * 24  # 24h
MAX_HISTORY_ENTRIES = 20  # 10 turns
CONTEXT_LOOKBACK = 10


def get_hr_context(*, telegram_id: int, text: str) -> dict:  # noqa: ARG001 — keeps signature stable for callers
    """Build the LangChain context dict from cached HR history."""
    history = cache.get(HISTORY_KEY_TEMPLATE.format(telegram_id=telegram_id), [])
    context: dict = {}
    if history:
        context["conversationHistory"] = history[-CONTEXT_LOOKBACK:]
    return context


def save_hr_history(*, telegram_id: int, user_msg: str, bot_msg: str) -> None:
    key = HISTORY_KEY_TEMPLATE.format(telegram_id=telegram_id)
    history = cache.get(key, [])
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_msg})
    cache.set(key, history[-MAX_HISTORY_ENTRIES:], timeout=HISTORY_TTL_SECONDS)
