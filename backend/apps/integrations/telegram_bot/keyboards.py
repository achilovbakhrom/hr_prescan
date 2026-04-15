"""Helpers for building Telegram inline keyboards.

Inline keyboards attach buttons to messages and emit ``callback_data`` strings
when pressed. We keep callback_data short (Telegram caps it at 64 bytes) and
use a colon-separated convention: ``<scope>:<action>:<arg1>:<arg2>``.
"""
from __future__ import annotations

from typing import Any

InlineKeyboard = dict[str, Any]


def button(*, text: str, callback_data: str | None = None, url: str | None = None) -> dict[str, Any]:
    """Build a single inline keyboard button.

    Either ``callback_data`` or ``url`` must be provided.
    """
    if callback_data is None and url is None:
        raise ValueError("button() requires callback_data or url")
    btn: dict[str, Any] = {"text": text}
    if callback_data is not None:
        if len(callback_data.encode("utf-8")) > 64:
            raise ValueError(f"callback_data exceeds 64 bytes: {callback_data!r}")
        btn["callback_data"] = callback_data
    if url is not None:
        btn["url"] = url
    return btn


def inline_keyboard(rows: list[list[dict[str, Any]]]) -> InlineKeyboard:
    """Wrap rows of buttons into a Telegram InlineKeyboardMarkup payload."""
    return {"inline_keyboard": rows}


def paginated_list(
    *,
    items: list[tuple[str, str]],
    page: int,
    page_size: int,
    page_callback_prefix: str,
    extra_rows: list[list[dict[str, Any]]] | None = None,
) -> InlineKeyboard:
    """Render a paginated list as an inline keyboard.

    Args:
        items: list of (label, callback_data) tuples for the visible items
        page: zero-indexed current page
        page_size: items per page
        page_callback_prefix: prefix for prev/next buttons (e.g. "vac:list")
            -> emitted as ``{prefix}:p<n>``
        extra_rows: optional rows appended below the pagination row
    """
    start = page * page_size
    end = start + page_size
    visible = items[start:end]

    rows: list[list[dict[str, Any]]] = [
        [button(text=label, callback_data=cb)] for label, cb in visible
    ]

    nav: list[dict[str, Any]] = []
    if page > 0:
        nav.append(button(text="◀ Prev", callback_data=f"{page_callback_prefix}:p{page - 1}"))
    if end < len(items):
        nav.append(button(text="Next ▶", callback_data=f"{page_callback_prefix}:p{page + 1}"))
    if nav:
        rows.append(nav)

    if extra_rows:
        rows.extend(extra_rows)

    return inline_keyboard(rows)
